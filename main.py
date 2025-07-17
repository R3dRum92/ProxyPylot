#!/usr/bin/env python3
import asyncio
import threading
from functools import partial
from typing import Optional

from app.db.session import init_db
from app.filter import ContentFilter
from app.GUI import ContentFilterGUI
from app.handler import ProxyHTTPRequestHandler
from app.thread import ThreadedHTTPProxy


def create_http_proxy(
    host: str = "localhost", port: int = 8080, filter: Optional[ContentFilter] = None
):
    """Create and start HTTP proxy server."""
    if filter is None:
        proxy = ThreadedHTTPProxy((host, port), ProxyHTTPRequestHandler)
    else:
        handler_class = partial(ProxyHTTPRequestHandler, content_filter=filter)

        proxy = ThreadedHTTPProxy((host, port), handler_class)

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
    asyncio.run(init_db())
    filter = ContentFilter()
    proxy_thread = threading.Thread(
        target=create_http_proxy, args=("localhost", 8080, filter), daemon=True
    )
    proxy_thread.start()
    app = ContentFilterGUI()
    app.run()
