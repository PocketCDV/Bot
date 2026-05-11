from datetime import datetime

from sqlalchemy import Column, UUID, DateTime, ForeignKey, Boolean, String
from sqlalchemy.orm import relationship

from app.assets.models.database.base import Base


class UserSettings(Base):
    """
    Database object for storing user settings.
    """

    __tablename__ = "user_settings"

    user_id = Column(UUID(True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    """
    User id.
    """

    locale = Column(String(8), nullable=True, default=None)
    """
    User's locale. Used to localize telegram responses.
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
