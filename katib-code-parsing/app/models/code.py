import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import Base


class Code(Base):
    __tablename__ = "codes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )
    versions = relationship("CodeVersion", back_populates="code", cascade="all, delete-orphan")


class CodeVersion(Base):
    __tablename__ = "code_versions"
    id = Column(Integer, primary_key=True, index=True)
    code_id = Column(Integer, ForeignKey("codes.id"), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    code = relationship("Code", back_populates="versions")
    parsing_results = relationship(
        "ParsingResult",
        back_populates="code_version",
        cascade="all, delete-orphan",
    )
