from contextlib import asynccontextmanager
from typing import Optional, List
from datetime import datetime

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

    
    # NEW TRAFFIC LOGGING METHODS
    async def log_traffic(
        self,
        site_name: str,
        ip_address: str,
        client_ip: Optional[str] = None,
        method: Optional[str] = None,
        status_code: Optional[int] = None,
        user_agent: Optional[str] = None
    ):
        """Log network traffic to the database."""
        async with get_db_session() as session:
            return await crud.log_traffic(
                session,
                site_name=site_name,
                ip_address=ip_address,
                client_ip=client_ip,
                method=method,
                status_code=status_code,
                user_agent=user_agent
            )

    async def get_traffic_logs(
        self,
        search_query: Optional[str] = None,
        limit: int = 1000,
        offset: int = 0
    ):
        """Get traffic logs from the database with optional search."""
        async with get_db_session() as session:
            return await crud.get_traffic_logs(session, search_query, limit, offset)

    async def get_traffic_count(self, search_query: Optional[str] = None):
        """Get the total count of traffic logs."""
        async with get_db_session() as session:
            return await crud.get_traffic_count(session, search_query)

    async def clear_old_traffic_logs(self, days_old: int = 30):
        """Clear traffic logs older than specified days."""
        async with get_db_session() as session:
            return await crud.clear_old_traffic_logs(session, days_old)

    # HELPER METHOD FOR PROXY INTEGRATION
    async def process_request(
        self,
        host: str,
        client_ip: str,
        method: str = "GET",
        user_agent: Optional[str] = None,
        resolved_ip: Optional[str] = None
    ):
        """Process a proxy request - check blocking and log traffic."""
        # Check if domain is blocked
        is_blocked = await self.is_domain_blocked(host, client_ip)
        
        if is_blocked:
            # Log blocked attempt
            await self.log_traffic(
                site_name=host,
                ip_address=resolved_ip or "blocked",
                client_ip=client_ip,
                method=method,
                status_code=403,  # Forbidden
                user_agent=user_agent
            )
            return {"allowed": False, "reason": "Domain blocked"}
        
        # Log allowed traffic
        await self.log_traffic(
            site_name=host,
            ip_address=resolved_ip or "unknown",
            client_ip=client_ip,
            method=method,
            status_code=200,  # OK
            user_agent=user_agent
        )
        
        return {"allowed": True, "reason": None}