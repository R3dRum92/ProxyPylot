from datetime import datetime, timedelta
from sqlalchemy.future import select
from .models import BlockedDomain
import ipaddress


async def add_blocked_domain(
    session,
    pattern: str,
    scope: str = "global",
    subnet: str = None,
    reason: str = None,
    added_by: str = None,
    expires_in_seconds: int = None
):
    expires_at = None
    if expires_in_seconds:
        expires_at = datetime.now(datetime.timezone.utc) + timedelta(seconds=expires_in_seconds)

    new_rule = BlockedDomain(
        pattern=pattern.lower(),
        scope=scope,
        subnet=subnet,
        reason=reason,
        added_by=added_by,
        expires_at=expires_at
    )
    session.add(new_rule)
    await session.commit()
    await session.refresh(new_rule)
    return new_rule

#active rules
async def get_active_rules(session):
    now = datetime.now(datetime.timezone.utc)
    stmt = select(BlockedDomain).where(
        (BlockedDomain.expires_at.is_(None)) | (BlockedDomain.expires_at > now)
    )
    result = await session.execute(stmt)
    return result.scalars().all()

#delete rules
async def delete_rule(session, rule_id: int):
    stmt = select(BlockedDomain).where(BlockedDomain.id == rule_id)
    result = await session.execute(stmt)
    rule = result.scalar_one_or_none()

    if rule:
        await session.delete(rule)
        await session.commit()

#find op
def ip_in_subnet(ip: str, subnet: str) -> bool:
    try:
        ip_obj = ipaddress.ip_address(ip)
        net_obj = ipaddress.ip_network(subnet, strict=False)
        return ip_obj in net_obj
    except ValueError:
        return False

async def is_domain_blocked(session, host: str, client_ip: str = None):
    now = datetime.utcnow()
    stmt = select(BlockedDomain).where(
        (BlockedDomain.expires_at.is_(None)) | (BlockedDomain.expires_at > now)
    )
    result = await session.execute(stmt)
    rules = result.scalars().all()

    host_lower = host.lower()
    for rule in rules:
        if rule.pattern in host_lower:
            if rule.scope == "global":
                return True, f"Blocked globally: {rule.pattern}"
            elif rule.scope == "subnet" and client_ip and rule.subnet:
                if ip_in_subnet(client_ip, rule.subnet):
                    return True, f"Blocked for subnet {rule.subnet}: {rule.pattern}"

    return False, None
