from datetime import datetime

from sqlalchemy import Column, UUID, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from uuid_extensions import uuid7

from app.assets.models.database.base import Base


class UserSettings(Base):
    """
    Database object for storing user settings.
    """

    __tablename__ = "user_settings"

    id = Column(UUID(True), primary_key=True, default=uuid7, nullable=False, index=True)
    """
    UUID.
    """

    user_id = Column(UUID(True), ForeignKey("users.id"), nullable=False)
    """
    User id.
    """

    upcoming_class_notifications_enabled = Column(Boolean, nullable=False, default=False)
    """
    Whether upcoming notifications are enabled.
    """

    daily_class_notifications_enabled = Column(Boolean(), nullable=False, default=False)
    """
    Whether daily notifications are enabled.
    """

    created_at = Column(DateTime(), nullable=False, default=datetime.now)
    """
    User's creation date.
    """

    updated_at = Column(DateTime(), nullable=True, onupdate=datetime.now)
    """
    User's last update date.
    """

    user = relationship("User", back_populates="settings")
    """
    User object related to settings.
    """
