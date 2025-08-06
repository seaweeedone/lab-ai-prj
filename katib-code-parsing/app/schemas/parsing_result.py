import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict


class ParsingResultVersionBase(BaseModel):
    content: Dict[str, Any]


class ParsingResultVersionCreate(ParsingResultVersionBase):
    pass


class ParsingResultVersionInDB(ParsingResultVersionBase):
    id: int
    version: int
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class ParsingResultBase(BaseModel):
    name: str


class ParsingResultCreate(ParsingResultBase):
    pass


class ParsingResultInDB(ParsingResultBase):
    id: int
    code_version_id: int
    created_at: datetime.datetime
    versions: List[ParsingResultVersionInDB] = []

    model_config = ConfigDict(from_attributes=True)
