from sqlalchemy import Column, Integer, String

from app.infrastructure.database.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)

    name = Column(String(50), unique=True, nullable=False)
