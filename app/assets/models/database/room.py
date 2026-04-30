from sqlalchemy import Column, String, Integer

from app.assets.models.database.base import Base


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
