import datetime
import os
import socket
import ssl
import threading
import urllib
from http.client import HTTPConnection, HTTPSConnection
from http.server import BaseHTTPRequestHandler

from app.cache import ProxyCache
from app.certificate import generate_signed_cert
from app.filter import ContentFilter
from utils.logger import logger

import asyncio
from app.db.session import AsyncSessionLocal
from app.db import crud


class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for proxy server."""

    def __init__(self, *args, **kwargs):
        self.cache = ProxyCache()
        self.filter = ContentFilter()
        super().__init__(*args, **kwargs)
    
    async def is_domain_blocked_in_db(self, host, client_ip):
        """Check in the database asynchronously."""
        async with AsyncSessionLocal() as session:
            is_blocked, reason = await crud.is_domain_blocked(session, host, client_ip)
            return is_blocked, reason

    def is_domain_blocked(self, host, client_ip):
        """Check both static filter and database."""
        # Check static filter first
        is_blocked, reason = self.filter.is_domain_blocked(host)
        if is_blocked:
            return True, reason

        # Then check database
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.is_domain_blocked_in_db(host, client_ip)
            )
            return result
        finally:
            loop.close()


    def do_CONNECT(self):
        """Handle CONNECT method for HTTPS tunneling."""
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

            # Check if domain is blocked
            is_blocked, block_reason = self.is_domain_blocked(host, self.client_address[0])
            if is_blocked:
                self.send_response(403)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(f"CONNECT blocked: {block_reason}".encode())
                return

            # Create connection to target server
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.settimeout(30)
            target_socket.connect((host, port))

            # Send 200 Connection established
            self.send_response(200, "Connection established")
            self.end_headers()

            # Get the underlying socket from the request
            client_socket = self.request

            # Start tunneling
            self._tunnel_data(client_socket, target_socket)

        except Exception as e:
            logger.error(f"[CONNECT ERROR] {e}")
            try:
                self.send_response(502)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(f"Connection failed: {str(e)}".encode())
            except:
                pass

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
        is_blocked, block_reason = self.is_domain_blocked(parsed_url.netloc, self.client_address[0])
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

    