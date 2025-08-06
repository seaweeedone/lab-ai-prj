from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.code import Code, CodeVersion
from app.models.parsing_result import ParsingResult
from app.schemas.code import CodeBase, CodeCreate


async def create_code(db: AsyncSession, code: CodeCreate) -> Code:
    db_code = Code(name=code.name)
    db.add(db_code)
    await db.commit()
    await db.refresh(db_code)

    db_code_version = CodeVersion(code_id=db_code.id, version=1, content=code.content)
    db.add(db_code_version)
    await db.commit()
    await db.refresh(db_code)

    # Fetch the code with its versions eagerly loaded
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(Code)
        .options(
            selectinload(Code.versions)
            .selectinload(CodeVersion.parsing_results)
            .selectinload(ParsingResult.versions)
        )
        .filter(Code.id == db_code.id)
    )
    db_code = result.scalars().first()

    return db_code


async def get_codes(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Code]:
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(Code)
        .options(
            selectinload(Code.versions)
            .selectinload(CodeVersion.parsing_results)
            .selectinload(ParsingResult.versions)
        )
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_code(db: AsyncSession, code_id: int) -> Optional[Code]:
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(Code)
        .options(
            selectinload(Code.versions)
            .selectinload(CodeVersion.parsing_results)
            .selectinload(ParsingResult.versions)
        )
        .filter(Code.id == code_id)
    )
    return result.scalars().first()


async def update_code(db: AsyncSession, code_id: int, code: CodeBase) -> Optional[Code]:
    db_code = await get_code(db, code_id)
    if db_code:
        db_code.name = code.name  # type: ignore
        await db.commit()
        await db.refresh(db_code)
    return db_code


async def delete_code(db: AsyncSession, code_id: int) -> Optional[Code]:
    db_code = await get_code(db, code_id)
    if db_code:
        await db.delete(db_code)
        await db.commit()
    return db_code
