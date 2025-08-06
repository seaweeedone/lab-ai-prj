from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.code import CodeVersion
from app.models.parsing_result import ParsingResult, ParsingResultVersion
from app.schemas.parsing_result import (
    ParsingResultBase,
    ParsingResultCreate,
    ParsingResultVersionCreate,
)
from app.services.llm_service import parse_code_with_llm


async def create_parsing_result(
    db: AsyncSession, code_version_id: int, result_create: ParsingResultCreate
) -> ParsingResult:
    """
    Creates a new parsing result for a given code version.
    This involves fetching the code content, parsing it with the LLM,
    and storing the result.
    """
    # Get the code content from the code version
    code_version = await db.get(CodeVersion, code_version_id)
    if not code_version:
        return None

    # Parse the code using the LLM service
    parsed_content = await parse_code_with_llm(str(code_version.content))

    # Create the ParsingResult and its first version
    db_result = ParsingResult(code_version_id=code_version_id, name=result_create.name)
    db.add(db_result)
    await db.commit()
    await db.refresh(db_result)

    db_result_version = ParsingResultVersion(
        parsing_result_id=db_result.id, version=1, content=parsed_content
    )
    db.add(db_result_version)
    await db.commit()
    await db.refresh(db_result)

    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(ParsingResult)
        .options(selectinload(ParsingResult.versions))
        .filter(ParsingResult.id == db_result.id)
    )
    db_result = result.scalars().first()

    return db_result


async def get_parsing_result(db: AsyncSession, result_id: int) -> Optional[ParsingResult]:
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(ParsingResult)
        .options(selectinload(ParsingResult.versions))
        .filter(ParsingResult.id == result_id)
    )
    return result.scalars().first()


async def update_parsing_result(
    db: AsyncSession, result_id: int, result: ParsingResultBase
) -> Optional[ParsingResult]:
    db_result = await get_parsing_result(db, result_id)
    if db_result:
        db_result.name = result.name  # type: ignore
        await db.commit()
        await db.refresh(db_result)
    return db_result


async def delete_parsing_result(db: AsyncSession, result_id: int) -> Optional[ParsingResult]:
    db_result = await get_parsing_result(db, result_id)
    if db_result:
        await db.delete(db_result)
        await db.commit()
    return db_result


async def create_parsing_result_version(
    db: AsyncSession, result_id: int, version: ParsingResultVersionCreate
) -> Optional[ParsingResultVersion]:
    # Check if the parent parsing result exists
    parent_result = await get_parsing_result(db, result_id)
    if not parent_result:
        return None

    result = await db.execute(
        select(ParsingResultVersion.version)
        .filter(ParsingResultVersion.parsing_result_id == result_id)
        .order_by(ParsingResultVersion.version.desc())
        .limit(1)
    )
    latest_version = result.scalars().first() or 0

    db_result_version = ParsingResultVersion(
        parsing_result_id=result_id,
        version=latest_version + 1,
        content=version.content,
    )
    db.add(db_result_version)
    await db.commit()
    await db.refresh(db_result_version)
    return db_result_version


async def delete_parsing_result_version(
    db: AsyncSession, result_id: int, version_id: int
) -> Optional[ParsingResultVersion]:
    db_version = await db.execute(
        select(ParsingResultVersion)
        .filter(ParsingResultVersion.parsing_result_id == result_id)
        .filter(ParsingResultVersion.id == version_id)
    )
    db_version = db_version.scalars().first()
    if db_version:
        await db.delete(db_version)
        await db.commit()
    return db_version
