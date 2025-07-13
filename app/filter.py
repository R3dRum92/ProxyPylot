class ContentFilter:
    """Content filtering and blocking functionality."""

    def __init__(self, blocked_domains=None, blocked_keywords=None):
        self.blocked_domains = blocked_domains or [
            "doubleclick.net",
            "googleadservices.com",
            "googlesyndication.com",
            "googletagmanager.com",
            "twitter.com",
        ]
        self.blocked_keywords = blocked_keywords or [
            "malware",
            "phishing",
            "spam",
            "virus",
            "adult",
        ]

    def is_domain_blocked(self, host):
        """Check if domain is in blocked list."""
        host_lower = host.lower()
        for blocked_domain in self.blocked_domains:
            if blocked_domain in host_lower:
                return True, f"Blocked domain: {blocked_domain}"
        return False, None

    def is_content_blocked(self, content):
        """Check if content contains blocked keywords."""
        if not content or not isinstance(content, str):
            return False, None
        content_lower = content.lower()
        for keyword in self.blocked_keywords:
            if keyword in content_lower:
                return True, f"Blocked keyword: {keyword}"
        return False, None
