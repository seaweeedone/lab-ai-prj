from .code import CodeInDB, CodeVersionInDB
from .parsing_result import ParsingResultInDB, ParsingResultVersionInDB

CodeInDB.update_forward_refs()
CodeVersionInDB.update_forward_refs()
ParsingResultInDB.update_forward_refs()
ParsingResultVersionInDB.update_forward_refs()
