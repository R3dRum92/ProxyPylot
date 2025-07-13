from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint
from sqlalchemy.sql import func
from .session import Base

class BlockedDomain(Base):
    __tablename__ = "blocked_domains"

    id = Column(Integer, primary_key=True, index=True)
    pattern = Column(String, nullable=False)
    scope = Column(String, nullable=False)
    subnet = Column(String, nullable=True)
    reason = Column(String, nullable=True)
    added_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("scope IN ('global', 'subnet')", name="scope_check"),
    )
