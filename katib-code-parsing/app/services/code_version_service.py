from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.code import CodeVersion
from app.schemas.code import CodeVersionCreate
from app.services.code_service import get_code as get_parent_code


async def create_code_version(
    db: AsyncSession, code_id: int, version: CodeVersionCreate
) -> CodeVersion:
    # Check if the parent code exists
    parent_code = await get_parent_code(db, code_id)
    if not parent_code:
        return None  # Indicate that the parent code does not exist

    # Get the latest version number for the code
    result = await db.execute(
        select(CodeVersion.version)
        .filter(CodeVersion.code_id == code_id)
        .order_by(CodeVersion.version.desc())
        .limit(1)
    )
    latest_version = result.scalars().first() or 0

    db_code_version = CodeVersion(
        code_id=code_id,
        version=latest_version + 1,
        content=version.content,
    )
    db.add(db_code_version)
    await db.commit()
    await db.refresh(db_code_version)

    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(CodeVersion)
        .options(selectinload(CodeVersion.parsing_results))
        .filter(CodeVersion.id == db_code_version.id)
    )
    db_code_version = result.scalars().first()

    return db_code_version


async def get_code_version(db: AsyncSession, version_id: int) -> Optional[CodeVersion]:
    result = await db.execute(select(CodeVersion).filter(CodeVersion.id == version_id))
    return result.scalars().first()


async def delete_code_version(db: AsyncSession, version_id: int) -> Optional[CodeVersion]:
    db_code_version = await get_code_version(db, version_id)
    if db_code_version:
        await db.delete(db_code_version)
        await db.commit()
    return db_code_version
