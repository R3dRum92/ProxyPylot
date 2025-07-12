import hashlib
import json
import os
import time


class ProxyCache:
    """Simple file-based cache for proxy responses."""

    def __init__(self, cache_dir="proxy_cache", max_age=3600):
        self.cache_dir = cache_dir
        self.max_age = max_age
        os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_key(self, url, headers=None):
        """Generate cache key from URL and relevant headers."""
        key_data = url
        if headers:
            key_data += str(headers.get("User-Agent", ""))
            key_data += str(headers.get("Accept", ""))
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, url, headers=None):
        """Get cached response if available and not expired."""
        cache_key = self._get_cache_key(url, headers)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")

        try:
            if os.path.exists(cache_file):
                with open(cache_file, "r") as f:
                    cached_data = json.load(f)

                if time.time() - cached_data["timestamp"] < self.max_age:
                    print(f"[CACHE HIT] {url}")
                    return cached_data
                else:
                    print(f"[CACHE EXPIRED] {url}")
                    os.remove(cache_file)
        except Exception as e:
            print(f"[CACHE ERROR] {e}")

        return None

    def set(self, url, response_data, headers=None):
        """Cache response data."""
        cache_key = self._get_cache_key(url, headers)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")

        try:
            cached_data = {
                "url": url,
                "timestamp": time.time(),
                "status_code": response_data.get("status_code"),
                "headers": response_data.get("headers"),
                "content": (
                    response_data.get("content").decode("utf-8", errors="ignore")
                    if isinstance(response_data.get("content"), bytes)
                    else response_data.get("content")
                ),
                "content_type": response_data.get("content_type"),
            }

            with open(cache_file, "w") as f:
                json.dump(cached_data, f)

            print(f"[CACHED] {url}")
        except Exception as e:
            print(f"[CACHE WRITE ERROR] {e}")
