import os
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from ssl import PROTOCOL_TLS_SERVER, SSLContext


class HTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

    daemon_threads = True
    allow_reuse_address = True


class CustomHTTPRequestHandler(BaseHTTPRequestHandler):
    """Custom HTTP request handler with basic functionality"""

    def do_GET(self):
        """Handle GET requests"""

        print(f"[{datetime.now()}] GET request from {self.client_address[0]}")

        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Threaded HTTPS Server</title>
            </head>
            <body>
                <h1>Welcome to the Threaded HTTPS Server!</h1>
                <p>This is a secure connection using SSL/TLS.</p>
                <p>Thread ID: {}</p>
                <p>Request from: {}</p>
                <p><a href="/status">Check server status</a></p>
            </body>
            </html>
            """.format(
                threading.current_thread().ident, self.client_address[0]
            )

            self.wfile.write(html_content.encode("utf-8"))

    # def do_POST(self):
    #     """Handle POST requests"""
    #     content_length = int(self.headers.get("Content-Length", 0))
    #     post_data = self.rfile.read(content_length)

    #     print(f"[{datetime.now()}] POST request from {self.client_address[0]}")
    #     print(f"Data received: {post_data.decode("utf-8", errors="ignore")}")

    #     self.send_response(200)
    #     self.send_header("")


def create_https_server(
    host="localhost", port=8443, certfile="server.crt", keyfile="server.key"
):
    """Create and start the threaded HTTPS server."""

    if not os.path.exists(certfile) or not os.path.exists(keyfile):
        print(
            f"Certificate files not found. Cannot create HTTPS server without certificate files."
        )

        return

    server = HTTPServer((host, port), CustomHTTPRequestHandler)

    context = SSLContext(PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=certfile, keyfile=keyfile)

    server.socket = context.wrap_socket(server.socket, server_side=True)

    print(f"Starting threaded HTTPS server on https://{host}:{port}")
    print(f"Certificate: {certfile}")
    print(f"Private key: {keyfile}")
    print("Press Ctrl+C to stop the server")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    HOST = "localhost"
    PORT = 8443

    create_https_server(HOST, PORT)
