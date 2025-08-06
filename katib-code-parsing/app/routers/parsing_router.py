from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.parsing_result import (
    ParsingResultBase,
    ParsingResultCreate,
    ParsingResultInDB,
    ParsingResultVersionCreate,
    ParsingResultVersionInDB,
)
from app.services import parsing_service

router = APIRouter()


@router.post(
    "/code-versions/{code_version_id}",
    response_model=ParsingResultInDB,
    status_code=201,
)
async def create_parsing_result(
    code_version_id: int,
    result_create: ParsingResultCreate,
    db: AsyncSession = Depends(get_db),
) -> ParsingResultInDB:
    db_result = await parsing_service.create_parsing_result(
        db=db, code_version_id=code_version_id, result_create=result_create
    )
    if db_result is None:
        raise HTTPException(status_code=404, detail="Code version not found")
    return db_result


@router.get("/results/{result_id}", response_model=ParsingResultInDB)
async def read_parsing_result(
    result_id: int, db: AsyncSession = Depends(get_db)
) -> ParsingResultInDB:
    db_result = await parsing_service.get_parsing_result(db, result_id=result_id)
    if db_result is None:
        raise HTTPException(status_code=404, detail="Parsing result not found")
    return db_result


@router.put("/results/{result_id}", response_model=ParsingResultInDB)
async def update_parsing_result(
    result_id: int,
    result: ParsingResultBase,
    db: AsyncSession = Depends(get_db),
) -> ParsingResultInDB:
    db_result = await parsing_service.update_parsing_result(db, result_id=result_id, result=result)
    if db_result is None:
        raise HTTPException(status_code=404, detail="Parsing result not found")
    return db_result


@router.delete("/results/{result_id}", status_code=204)
async def delete_parsing_result(result_id: int, db: AsyncSession = Depends(get_db)) -> None:
    db_result = await parsing_service.delete_parsing_result(db, result_id=result_id)
    if db_result is None:
        raise HTTPException(status_code=404, detail="Parsing result not found")
    return


@router.post(
    "/results/{result_id}/versions",
    response_model=ParsingResultVersionInDB,
    status_code=201,
)
async def create_parsing_result_version(
    result_id: int,
    version: ParsingResultVersionCreate,
    db: AsyncSession = Depends(get_db),
) -> ParsingResultVersionInDB:
    db_result_version = await parsing_service.create_parsing_result_version(
        db=db, result_id=result_id, version=version
    )
    if db_result_version is None:
        raise HTTPException(status_code=404, detail="Parsing result not found")
    return db_result_version


@router.delete("/results/{result_id}/versions/{version_id}", status_code=204)
async def delete_parsing_result_version(
    result_id: int, version_id: int, db: AsyncSession = Depends(get_db)
) -> None:
    db_result_version = await parsing_service.delete_parsing_result_version(
        db, result_id=result_id, version_id=version_id
    )
    if db_result_version is None:
        raise HTTPException(status_code=404, detail="Parsing result version not found")
    return
