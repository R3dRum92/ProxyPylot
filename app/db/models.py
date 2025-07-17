from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import CheckConstraint, Column, DateTime, Integer, String
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

    @property
    def duration_hours(self) -> Optional[int]:
        """Calculates the duration in hours based on created_at and expires_at."""
        if self.expires_at is None:
            return None  # Permanent block
        if self.created_at is None:
            # This scenario should ideally not happen if created_at is always set
            return None

        # Ensure both are timezone-aware if func.now() is timezone-aware
        # Or make them naive for calculation if consistent

        time_difference: timedelta = self.expires_at - self.created_at
        return int(time_difference.total_seconds() / 3600)  # Convert seconds to hours


class TrafficLog(Base):
    __tablename__ = "traffic_logs"

    id = Column(Integer, primary_key=True, index=True)
    time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    method = Column(String, nullable=False)
    url = Column(String, nullable=False)
    client_ip = Column(String, nullable=False)
