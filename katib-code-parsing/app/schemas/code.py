import datetime

# Forward reference to handle circular dependency
from typing import List

from pydantic import BaseModel, ConfigDict

from .parsing_result import ParsingResultInDB


class CodeVersionBase(BaseModel):
    content: str


class CodeVersionCreate(CodeVersionBase):
    pass


class CodeVersionInDB(CodeVersionBase):
    id: int
    version: int
    created_at: datetime.datetime
    parsing_results: List["ParsingResultInDB"] = []

    model_config = ConfigDict(from_attributes=True)


class CodeBase(BaseModel):
    name: str


class CodeCreate(CodeBase):
    content: str


class CodeInDB(CodeBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    versions: List[CodeVersionInDB] = []

    model_config = ConfigDict(from_attributes=True)
