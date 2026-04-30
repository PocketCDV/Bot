from sqlalchemy import Column, String, Integer

from app.assets.models.database.base import Base


class Teacher(Base):
    """
    Database teacher object which represents a CDV professor (Only ID and full name, no personal data).
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
