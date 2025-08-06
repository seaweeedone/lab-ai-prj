from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.code import CodeVersionCreate, CodeVersionInDB
from app.services import code_version_service

router = APIRouter()


@router.post("/", response_model=CodeVersionInDB, status_code=201)
async def create_code_version(
    code_id: int,
    version: CodeVersionCreate,
    db: AsyncSession = Depends(get_db),
) -> CodeVersionInDB:
    db_code_version = await code_version_service.create_code_version(
        db=db, code_id=code_id, version=version
    )
    if db_code_version is None:
        raise HTTPException(status_code=404, detail="Parent code not found")
    return db_code_version


@router.delete("/{version_id}", status_code=204)
async def delete_code_version(version_id: int, db: AsyncSession = Depends(get_db)) -> None:
    db_code_version = await code_version_service.delete_code_version(db, version_id=version_id)
    if db_code_version is None:
        raise HTTPException(status_code=404, detail="Code version not found")
    return
