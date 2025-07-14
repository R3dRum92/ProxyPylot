from contextlib import asynccontextmanager
from typing import Optional

from app.db import crud
from app.db.session import AsyncSessionLocal


@asynccontextmanager
async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session


class ContentFilter:
    """Content filtering and blocking functionality."""

    def __init__(self, blocked_keywords=None):
        self.blocked_keywords = blocked_keywords or [
            "malware",
            "phishing",
            "spam",
            "virus",
            "adult",
        ]

    async def is_domain_blocked(self, host, client_ip: Optional[str] = None):
        """Check if the host matches any active block rule from the database"""
        async with get_db_session() as session:
            return await crud.is_domain_blocked(session, host, client_ip)

    def is_content_blocked(self, content):
        """Check if content contains blocked keywords."""
        if not content or not isinstance(content, str):
            return False, None
        content_lower = content.lower()
        for keyword in self.blocked_keywords:
            if keyword in content_lower:
                return True, f"Blocked keyword: {keyword}"
        return False, None

    async def add_block_rule(self, **kwargs):
        async with get_db_session() as session:
            return await crud.add_blocked_domain(session, **kwargs)

    async def delete_block_rule(self, rule_id: int):
        async with get_db_session() as session:
            return await crud.delete_rule(session, rule_id)

    async def update_block_rule(self, rule_id: int, **kwargs):
        async with get_db_session() as session:
            return await crud.update_blocked_domain(session, rule_id, **kwargs)

    async def list_block_rules(self):
        async with get_db_session() as session:
            return await crud.get_active_rules(session)
