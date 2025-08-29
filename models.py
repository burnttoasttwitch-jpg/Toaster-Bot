from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    discord_id = Column(String, unique=True, index=True)
    warnings = relationship("Warning", back_populates="user", cascade="all, delete")
    notes = relationship("Note", back_populates="user", cascade="all, delete")

class Warning(Base):
    __tablename__ = "warnings"
    id = Column(Integer, primary_key=True)
    reason = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="warnings")

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="notes")
