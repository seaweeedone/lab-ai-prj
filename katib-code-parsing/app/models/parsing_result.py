import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class ParsingResult(Base):
    __tablename__ = "parsing_results"
    id = Column(Integer, primary_key=True, index=True)
    code_version_id = Column(Integer, ForeignKey("code_versions.id"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    code_version = relationship("CodeVersion", back_populates="parsing_results")
    versions = relationship(
        "ParsingResultVersion",
        back_populates="parsing_result",
        cascade="all, delete-orphan",
    )


class ParsingResultVersion(Base):
    __tablename__ = "parsing_result_versions"
    id = Column(Integer, primary_key=True, index=True)
    parsing_result_id = Column(Integer, ForeignKey("parsing_results.id"), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(JSON, nullable=False)  # JSON content
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    parsing_result = relationship("ParsingResult", back_populates="versions")
