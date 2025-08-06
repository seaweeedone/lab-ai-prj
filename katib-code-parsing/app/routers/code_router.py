from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.code import CodeBase, CodeCreate, CodeInDB
from app.services import code_service

router = APIRouter()


@router.post("/", response_model=CodeInDB, status_code=201)
async def create_code(code: CodeCreate, db: AsyncSession = Depends(get_db)) -> CodeInDB:
    return await code_service.create_code(db=db, code=code)


@router.get("/", response_model=List[CodeInDB])
async def read_codes(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
) -> List[CodeInDB]:
    codes = await code_service.get_codes(db, skip=skip, limit=limit)
    return [CodeInDB.model_validate(code) for code in codes]


@router.get("/{code_id}", response_model=CodeInDB)
async def read_code(code_id: int, db: AsyncSession = Depends(get_db)) -> CodeInDB:
    db_code = await code_service.get_code(db, code_id=code_id)
    if db_code is None:
        raise HTTPException(status_code=404, detail="Code not found")
    return db_code


@router.put("/{code_id}", response_model=CodeInDB)
async def update_code(code_id: int, code: CodeBase, db: AsyncSession = Depends(get_db)) -> CodeInDB:
    db_code = await code_service.update_code(db, code_id=code_id, code=code)
    if db_code is None:
        raise HTTPException(status_code=404, detail="Code not found")
    return db_code


@router.delete("/{code_id}", status_code=204)
async def delete_code(code_id: int, db: AsyncSession = Depends(get_db)) -> None:
    db_code = await code_service.delete_code(db, code_id=code_id)
    if db_code is None:
        raise HTTPException(status_code=404, detail="Code not found")
    return
