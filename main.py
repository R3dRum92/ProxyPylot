#!/usr/bin/env python3
from app.handler import ProxyHTTPRequestHandler
from app.thread import ThreadedHTTPProxy


def create_http_proxy(host="localhost", port=8080):
    """Create and start HTTP proxy server."""
    proxy = ThreadedHTTPProxy((host, port), ProxyHTTPRequestHandler)

    print(f"Starting HTTP Proxy Server on http://{host}:{port}")
    print(f"Admin interface: http://{host}:{port}/proxy-admin")
    print("Configure your browser to use this proxy server:")
    print(f"  HTTP Proxy: {host}:{port}")
    print(f"  HTTPS Proxy: {host}:{port}")
    print("Press Ctrl+C to stop the server")

    try:
        proxy.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down proxy server...")
        proxy.shutdown()
        proxy.server_close()


if __name__ == "__main__":
    create_http_proxy("localhost", 8080)
