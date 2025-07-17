import asyncio
import datetime
import hashlib
import os
import re
import socket
import ssl
import threading
import urllib
from http.client import HTTPConnection, HTTPSConnection
from http.server import BaseHTTPRequestHandler
from typing import Optional

from app.db import crud
from app.filter import ContentFilter
from utils.logger import logger


class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for proxy server."""

    def __init__(self, *args, content_filter=None, **kwargs):
        if content_filter:
            self.filter = content_filter
        else:
            self.filter = ContentFilter()
        super().__init__(*args, **kwargs)

    def do_CONNECT(self):
        """Handle CONNECT method for MITM HTTPS interception."""
        try:
            # Parse host and port
            host_port = self.path.split(":")
            if len(host_port) == 2:
                host, port = host_port[0], int(host_port[1])
            else:
                host, port = host_port[0], 443

            logger.info(
                f"[{datetime.datetime.now()}] CONNECT {host}:{port} from {self.client_address[0]}"
            )

            try:
                asyncio.run(
                    crud.add_traffic_log("CONNECT", host, self.client_address[0])
                )
            except Exception as e:
                logger.error(f"[TRAFFIC LOG ERROR] {e}")

            # Check if domain is blocked
            is_blocked, block_reason = self.is_domain_blocked(
                host, self.client_address[0]
            )
            if is_blocked:
                self.send_response(403)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(f"CONNECT blocked: {block_reason}".encode())
                return

            # Create the folder to store certs if missing
            os.makedirs("certs", exist_ok=True)
            cert_file = f"certs/{host}.crt"
            key_file = f"certs/{host}.key"

            # Check if we already have a signed cert for this host
            if not (os.path.exists(cert_file) and os.path.exists(key_file)):
                from app.certificate import generate_signed_cert

                generate_signed_cert(
                    domain=host,
                    ca_cert_file="proxy_ca.crt",
                    ca_key_file="proxy_ca.key",
                    out_cert_file=cert_file,
                    out_key_file=key_file,
                )
                logger.info(f"Generated new MITM cert for {host}")

            # Send 200 Connection established to browser
            self.send_response(200, "Connection established")
            self.end_headers()

            client_socket = self.request

            # Wrap client socket with our fake cert -> intercept TLS
            client_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            client_context.load_cert_chain(certfile=cert_file, keyfile=key_file)
            client_ssl = client_context.wrap_socket(client_socket, server_side=True)

            logger.info(f"TLS handshake completed with client for {host}")

            # Connect to target server with real TLS
            server_plain = socket.create_connection((host, port), timeout=30)
            server_context = ssl.create_default_context()
            server_ssl = server_context.wrap_socket(server_plain, server_hostname=host)

            logger.info(f"TLS handshake completed with target {host}")

            # Start MITM proxying
            self._mitm_tunnel_data(client_ssl, server_ssl, host=host)

        except Exception as e:
            logger.error(f"[CONNECT ERROR] {e}")
            try:
                self.send_response(502)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(f"Connection failed: {str(e)}".encode())
            except:
                pass

    def _mitm_tunnel_data(self, client_ssl, server_ssl, host=None):
        """Tunnel data between client (browser) and target server (with decryption)."""

        def forward(source, destination, direction, host=host):
            try:
                source.settimeout(None)
                destination.settimeout(None)
                buffer = b""
                headers_parsed = False
                content_length = None
                is_chunked = False
                body = b""
                while True:
                    data = source.recv(4096)
                    if not data:
                        break

                    destination.sendall(data)

                    if direction == "C->S":
                        try:
                            # Only do this if you want to see human-readable HTTP data
                            decoded = data.decode("utf-8", errors="ignore")
                            logger.info(
                                f"[HTTPS REQUEST] {decoded[:300]}"
                            )  # Log first 300 chars
                        except Exception as e:
                            logger.debug(f"[C->S decode error] {e}")
                    elif direction == "S->C":
                        buffer += data
                        if not headers_parsed:
                            if b"\r\n\r\n" in buffer:
                                headers_parsed = True
                                header_part, remaining = buffer.split(b"\r\n\r\n", 1)
                                headers = header_part.decode("iso-8859-1")

                                match = re.search(
                                    r"Content-Length: (\d+)", headers, re.IGNORECASE
                                )
                                if match:
                                    content_length = int(match.group(1))

                                if "Transfer-Encoding: chunked" in headers:
                                    is_chunked = True

                                body += remaining

                                if content_length is None and not is_chunked:
                                    break
                            else:
                                body += data

                            if content_length is not None:
                                if len(body) >= content_length:
                                    break
                            elif is_chunked:
                                # Crude end-of-chunk check (may need better parsing)
                                if b"0\r\n\r\n" in body:
                                    break

            except Exception as e:
                logger.info(f"[MITM {direction}] closed: {e}")
            finally:
                if direction == "S->C" and buffer:
                    try:
                        # Extract URL if possible, or pass "/" as dummy
                        self.cache_https_response(buffer, host=host, url="/")
                    except Exception as e:
                        logger.warning(f"Failed to cache response: {e}")
                try:
                    source.close()
                except:
                    pass
                try:
                    destination.close()
                except:
                    pass

        c2s = threading.Thread(
            target=forward, args=(client_ssl, server_ssl, "C->S"), daemon=True
        )
        s2c = threading.Thread(
            target=forward, args=(server_ssl, client_ssl, "S->C"), daemon=True
        )

        c2s.start()
        s2c.start()

        c2s.join()
        s2c.join()

    def cache_https_response(self, buffer: bytes, host: str, url: str):
        cache_key = hashlib.sha256(f"{host}{url}".encode()).hexdigest()

        cache_path = f"cache/{cache_key}.resp"
        os.makedirs("cache", exist_ok=True)

        with open(cache_path, "wb") as f:
            f.write(buffer)

        logger.info(f"[CACHE] Saved response to {cache_path}")

    def _read_http_message(self, sock):
        """
        Read one full HTTP/1.1 message (request or response) from a socket,
        handling both Content-Length and Transfer-Encoding: chunked.
        """

        # Step 1: Read headers
        data = b""
        while b"\r\n\r\n" not in data:
            chunk = sock.recv(4096)
            if not chunk:
                return None
            data += chunk

        header_end = data.find(b"\r\n\r\n") + 4
        headers = data[:header_end]
        body = data[header_end:]

        # Step 2: Parse headers
        headers_text = headers.decode("iso-8859-1")
        lines = headers_text.split("\r\n")
        headers_dict = {}
        for line in lines[1:]:
            if ":" in line:
                key, val = line.split(":", 1)
                headers_dict[key.strip().lower()] = val.strip().lower()

        # Step 3: Decide body transfer
        if "content-length" in headers_dict:
            length = int(headers_dict["content-length"])
            while len(body) < length:
                body += sock.recv(4096)
            return headers + body

        elif headers_dict.get("transfer-encoding") == "chunked":
            # Handle chunked
            body += self._read_chunked_body(sock, body)
            return headers + body

        else:
            # No body
            return headers

    def _read_chunked_body(self, sock, already_read=b""):
        data = already_read
        body = b""

        def read_line():
            nonlocal data
            while b"\r\n" not in data:
                more = sock.recv(4096)
                if not more:
                    return None
                data += more
            idx = data.find(b"\r\n")
            line = data[:idx]
            data = data[idx + 2 :]
            return line

        while True:
            # Read chunk size line
            size_line = read_line()
            if size_line is None:
                break
            try:
                chunk_size = int(size_line.strip(), 16)
            except ValueError:
                break

            if chunk_size == 0:
                # Read trailer and final CRLF
                while True:
                    trailer_line = read_line()
                    if trailer_line in (b"", None):
                        break
                break

            # Read chunk data
            while len(data) < chunk_size + 2:
                more = sock.recv(4096)
                if not more:
                    return body
                data += more

            body += data[:chunk_size]
            data = data[chunk_size + 2 :]  # skip CRLF

        return body

    def is_domain_blocked(self, domain: str, client_ip: Optional[str] = None):
        try:
            domain_only = domain.split(":")[0]
            return asyncio.run(self.filter.is_domain_blocked(domain_only, client_ip))
        except Exception as e:
            logger.error(f"[BLOCK CHECK ERROR] {e}")
            return False, ""

    def _tunnel_data(self, client_socket, target_socket):
        """Tunnel data between client and target server."""

        def forward_data(source, destination, direction):
            try:
                source.settimeout(None)
                destination.settimeout(None)
                while True:
                    data = source.recv(4096)
                    if not data:
                        break
                    destination.send(data)
            except Exception as e:
                logger.info(f"[TUNNEL {direction}] Connection closed: {e}")
            finally:
                try:
                    source.close()
                except:
                    pass
                try:
                    destination.close()
                except:
                    pass

        # Start forwarding in both directions
        client_to_target = threading.Thread(
            target=forward_data,
            args=(client_socket, target_socket, "C->T"),
            daemon=True,
        )
        target_to_client = threading.Thread(
            target=forward_data,
            args=(target_socket, client_socket, "T->C"),
            daemon=True,
        )

        client_to_target.start()
        target_to_client.start()

        # Wait for connections to close
        client_to_target.join()
        target_to_client.join()

    def do_GET(self):
        """Handle GET requests."""
        self._handle_http_request("GET")

    def do_POST(self):
        """Handle POST requests."""
        self._handle_http_request("POST")

    def do_PUT(self):
        """Handle PUT requests."""
        self._handle_http_request("PUT")

    def do_DELETE(self):
        """Handle DELETE requests."""
        self._handle_http_request("DELETE")

    def _handle_http_request(self, method):
        """Handle HTTP requests (non-CONNECT)."""
        url = self.path

        # Handle proxy admin interface
        if url.startswith("/proxy-admin"):
            self._handle_admin_request()
            return

        # Ensure URL is absolute
        if not url.startswith("http"):
            url = f"http://{self.headers.get('Host', 'localhost')}{url}"

        logger.info(
            f"[{datetime.datetime.now()}] {method} {url} from {self.client_address[0]}"
        )

        # Parse URL
        parsed_url = urllib.parse.urlparse(url)

        # Check if domain is blocked
        is_blocked, block_reason = self.is_domain_blocked(
            parsed_url.netloc, self.client_address[0]
        )
        if is_blocked:
            self._send_blocked_response(block_reason)
            return

        # Try cache for GET requests
        if method == "GET":
            cached_response = self.cache.get(url, dict(self.headers))
            if cached_response:
                self._send_cached_response(cached_response)
                return

        # Forward request
        try:
            response_data = self._forward_http_request(method, url)

            logger.info(response_data)

            if response_data:
                # Filter content
                if self._should_filter_content(response_data):
                    self._send_blocked_response("Content filtered")
                    return

                # Cache successful GET responses
                if method == "GET" and response_data.get("status_code") == 200:
                    self.cache.set(url, response_data, dict(self.headers))

                # Send response
                self._send_response(response_data)
            else:
                self._send_error_response(502, "Bad Gateway")

        except Exception as e:
            logger.error(f"[HTTP ERROR] {e}")
            self._send_error_response(500, f"Proxy Error: {str(e)}")

    def _forward_http_request(self, method, url):
        """Forward HTTP request to target server."""
        parsed_url = urllib.parse.urlparse(url)

        # Create SSL context that doesn't verify certificates
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # Determine connection type
        if parsed_url.scheme == "https":
            conn = HTTPSConnection(parsed_url.netloc, timeout=30, context=ssl_context)
        else:
            conn = HTTPConnection(parsed_url.netloc, timeout=30)

        try:
            # Prepare request path
            path = parsed_url.path or "/"
            if parsed_url.query:
                path += f"?{parsed_url.query}"

            # Prepare headers
            headers = dict(self.headers)
            headers.pop("Connection", None)
            headers.pop("Proxy-Connection", None)
            headers.pop("Transfer-Encoding", None)
            headers.pop("Proxy-Authorization", None)

            # Read request body
            body = None
            if method in ["POST", "PUT"] and "Content-Length" in headers:
                content_length = int(headers["Content-Length"])
                body = self.rfile.read(content_length)

            # Make request
            conn.request(method, path, body, headers)
            response = conn.getresponse()

            # Read response
            response_content = response.read()
            response_headers = dict(response.getheaders())

            return {
                "status_code": response.status,
                "reason": response.reason,
                "headers": response_headers,
                "content": response_content,
                "content_type": response_headers.get("Content-Type", ""),
            }

        except Exception as e:
            logger.error(f"[FORWARD ERROR] {e}")
            return None

        finally:
            conn.close()

    def _should_filter_content(self, response_data):
        """Check if content should be filtered."""
        content_type = response_data.get("content_type", "")

        # Check content for blocked keywords (only for text content)
        if content_type.startswith("text/"):
            try:
                content = response_data.get("content", b"").decode(
                    "utf-8", errors="ignore"
                )
                is_blocked, _ = self.filter.is_content_blocked(content)
                return is_blocked
            except:
                pass

        return False

    def _send_response(self, response_data):
        """Send response to client."""
        self.send_response(
            response_data["status_code"], response_data.get("reason", "")
        )

        # Send headers
        for key, value in response_data.get("headers", {}).items():
            if key.lower() not in ["connection", "transfer-encoding"]:
                self.send_header(key, value)

        self.end_headers()

        # Send content
        content = response_data.get("content", b"")
        if isinstance(content, str):
            content = content.encode("utf-8")

        self.wfile.write(content)

    def _send_cached_response(self, cached_data):
        """Send cached response to client."""
        self.send_response(cached_data["status_code"])

        for key, value in cached_data.get("headers", {}).items():
            if key.lower() not in ["connection", "transfer-encoding"]:
                self.send_header(key, value)

        self.send_header("X-Proxy-Cache", "HIT")
        self.end_headers()

        content = cached_data.get("content", "")
        if isinstance(content, str):
            content = content.encode("utf-8")

        self.wfile.write(content)

    def _send_blocked_response(self, reason):
        """Send blocked response."""
        self.send_response(403)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        blocked_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Content Blocked</title>
        </head>
        <body>
            <h1>Access Blocked</h1>
            <p><strong>Reason:</strong> {reason}</p>
            <p><strong>URL:</strong> {self.path}</p>
            <p><strong>Time:</strong> {datetime.datetime.now()}</p>
        </body>
        </html>
        """

        self.wfile.write(blocked_html.encode("utf-8"))

    def _send_error_response(self, code, message):
        """Send error response."""
        self.send_response(code)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Proxy Error</title>
        </head>
        <body>
            <h1>Proxy Error {code}</h1>
            <p>{message}</p>
            <p>URL: {self.path}</p>
        </body>
        </html>
        """

        self.wfile.write(error_html.encode("utf-8"))

    def _handle_admin_request(self):
        """Handle proxy admin interface."""
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        admin_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Proxy Server Admin</title>
        </head>
        <body>
            <h1>Proxy Server Status</h1>
            <p><strong>Status:</strong> Running</p>
            <p><strong>Active Threads:</strong> {threading.active_count()}</p>
            <p><strong>Cache Directory:</strong> {self.cache.cache_dir}</p>
            <p><strong>Time:</strong> {datetime.datetime.now()}</p>
            
            <h3>Blocked Domains</h3>
            <ul>
                {''.join(f'<li>{domain}</li>' for domain in self.filter.blocked_domains)}
            </ul>
        </body>
        </html>
        """

        self.wfile.write(admin_html.encode("utf-8"))

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass
        pass
        pass
        pass
