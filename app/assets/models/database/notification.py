from datetime import datetime

from sqlalchemy import Column, UUID, ForeignKey, DateTime, BigInteger, Enum
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from uuid_extensions import uuid7

from app.assets.enums.notification_kind import NotificationKind
from app.assets.models.database.base import Base


class Notification(Base):
    """
    Database notification object. Represents an upcoming notification for specific user.
    """

    __tablename__ = "notifications"

    id = Column(UUID(True), primary_key=True, default=uuid7, nullable=False, index=True)
    """
    UUID.
    """

    user_id = Column(UUID(True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    """
    User id.
    """

    telegram_id = Column(BigInteger(), nullable=False)
    """
    User's telegram ID.
    """

    kind = Column(Enum(NotificationKind), nullable=False)
    """
    Notification kind.
    """

    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)
    """
    When the notification must be sent.
    """

    data = Column(JSON(), nullable=False)
    """
    Notification data. Specific to kind, basically a JSON of DailyScheduleRecord or ClassRecord.
    """

    created_at = Column(DateTime(), nullable=False, default=datetime.now)
    """
    User's creation date.
    """

    updated_at = Column(DateTime(), nullable=True, onupdate=datetime.now)
    """
    User's last update date.
    """

    user = relationship("User", back_populates="notifications")
    """
    User object related to notifications.
    """
