import ipaddress
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .models import BlockedDomain


async def add_blocked_domain(
    session: AsyncSession,
    pattern: str,
    scope: str = "global",
    subnet: Optional[str] = None,
    reason: Optional[str] = None,
    added_by: Optional[str] = None,
    expires_in_seconds: Optional[int] = None,
    duration_hours: Optional[int] = None,
    
) -> BlockedDomain:
    expires_at = None
    if expires_in_seconds:
        expires_at = datetime.now(datetime.timezone.utc) + timedelta(
            seconds=expires_in_seconds
        )

    new_rule = BlockedDomain(
        pattern=pattern.lower(),
        scope=scope,
        subnet=subnet,
        reason=reason,
        added_by=added_by,
        expires_at=expires_at,
    )
    session.add(new_rule)
    await session.commit()
    await session.refresh(new_rule)
    return new_rule


# active rules
async def get_active_rules(session: AsyncSession) -> List[BlockedDomain]:
    now = datetime.now(timezone.utc)
    stmt = select(BlockedDomain).where(
        (BlockedDomain.expires_at.is_(None)) | (BlockedDomain.expires_at > now)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def update_blocked_domain(
    session: AsyncSession,
    rule_id: int,
    pattern: Optional[str] = None,
    scope: Optional[str] = None,
    subnet: Optional[str] = None,
    reason: Optional[str] = None,
    added_by: Optional[str] = None,
    expires_in_seconds: Optional[int] = None,
) -> Optional[BlockedDomain]:
    result = await session.execute(
        select(BlockedDomain).where(BlockedDomain.id == rule_id)
    )
    rule = result.scalar_one_or_none()

    if not rule:
        return None

    if pattern:
        rule.pattern = pattern.lower()
    if scope:
        rule.scope = scope
    if subnet:
        rule.subnet = subnet
    if reason:
        rule.reason = reason
    if added_by:
        rule.added_by = added_by
    if expires_in_seconds is not None:
        rule.expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=expires_in_seconds
        )

    await session.commit()
    await session.refresh(rule)
    return rule


# delete rules
async def delete_rule(session: AsyncSession, rule_id: int) -> None:
    stmt = select(BlockedDomain).where(BlockedDomain.id == rule_id)
    result = await session.execute(stmt)
    rule = result.scalar_one_or_none()

    if rule:
        await session.delete(rule)
        await session.commit()


# find op
def ip_in_subnet(ip: str, subnet: str) -> bool:
    try:
        ip_obj = ipaddress.ip_address(ip)
        net_obj = ipaddress.ip_network(subnet, strict=False)
        return ip_obj in net_obj
    except ValueError:
        return False


async def is_domain_blocked(
    session: AsyncSession, host: str, client_ip: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    now = datetime.now(timezone.utc)
    stmt = select(BlockedDomain).where(
        (BlockedDomain.expires_at.is_(None)) | (BlockedDomain.expires_at > now)
    )
    result = await session.execute(stmt)
    rules = result.scalars().all()

    # SELECT * FROM BlockedDomain WHERE expires_at IS NULL || expires_at > now

    host_lower = host.lower()
    for rule in rules:
        if rule.pattern in host_lower:
            if rule.scope == "global":
                return True, f"Blocked globally: {rule.pattern}"
            elif rule.scope == "subnet" and client_ip and rule.subnet:
                if ip_in_subnet(client_ip, rule.subnet):
                    return True, f"Blocked for subnet {rule.subnet}: {rule.pattern}"

    return False, None
