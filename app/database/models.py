from datetime import datetime

from sqlalchemy import Column, UUID, String, DateTime, BigInteger, Integer
from sqlalchemy.orm import declarative_base
from uuid_extensions import uuid7

Base = declarative_base()


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

    locale = Column(String(8), nullable=True, default=None)
    """
    User's locale. Used to localize telegram responses.
    """

    created_at = Column(DateTime(), nullable=False, default=datetime.now)
    """
    User's creation date.
    """

    updated_at = Column(DateTime(), nullable=True, onupdate=datetime.now)
    """
    User's last update date.
    """


class Room(Base):
    """
    Database room object which represents CDV classroom.
    """

    __tablename__ = "rooms"

    id = Column(Integer(), primary_key=True, nullable=False, index=True, autoincrement=False)
    """
    Room ID.
    """

    name = Column(String(64), nullable=False)
    """
    Room display name.
    """


class Teacher(Base):
    """
    Database room object which represents CDV professor (Only ID and full name, no personal data).
    """

    __tablename__ = "teachers"

    id = Column(Integer(), primary_key=True, nullable=False, index=True, autoincrement=False)
    """
    Teacher ID.
    """

    full_name = Column(String(64), nullable=False)
    """
    Teacher full name.
    """
