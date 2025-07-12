from http.server import HTTPServer
from socketserver import ThreadingMixIn


class ThreadedHTTPProxy(ThreadingMixIn, HTTPServer):
    """Threaded HTTP proxy server with HTTPS tunneling support."""

    daemon_threads = True
    allow_reuse_address = True
