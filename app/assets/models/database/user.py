from datetime import datetime

from sqlalchemy import Column, UUID, String, DateTime, BigInteger
from sqlalchemy.orm import relationship
from uuid_extensions import uuid7

from app.assets.models.database.base import Base


class User(Base):
    """
    Database user object.
    """

    __tablename__ = "users"

    id = Column(UUID(True), primary_key=True, default=uuid7, nullable=False, index=True)
    """
    UUID.
    """

    telegram_id = Column(BigInteger(), unique=True, nullable=False, index=True)
    """
    User's telegram ID.
    """

    first_name = Column(String(64), nullable=False)
    """
    First name from telegram.
    """

    created_at = Column(DateTime(), nullable=False, default=datetime.now)
    """
    User's creation date.
    """

    updated_at = Column(DateTime(), nullable=True, onupdate=datetime.now)
    """
    User's last update date.
    """

    settings = relationship("UserSettings", back_populates="user", uselist=False)
    """
    Settings object related to user.
    """
