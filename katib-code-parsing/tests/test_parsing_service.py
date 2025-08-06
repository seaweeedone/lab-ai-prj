import pytest
import pytest_asyncio
from unittest.mock import AsyncMock
from typing import AsyncGenerator
from pytest import MonkeyPatch

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models import Base, Code, CodeVersion
from app.schemas.parsing_result import ParsingResultCreate
from app.services import parsing_service, llm_service

# In-memory SQLite database for testing
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

# Mock LLM response
MOCK_LLM_RESPONSE = {
    "name": "test_code",
    "framework": "pytest",
    "metric": ["accuracy"],
    "parameter": "--test-param",
    "model_block": "def test_model(): pass",
    "data_block": "def test_data(): pass",
}


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_create_parsing_result_with_mock_llm(
    db_session: AsyncSession, monkeypatch: MonkeyPatch
) -> None:
    # 1. Arrange: Create test data and mock the LLM service

    # Mock the LLM service function
    mock_parse = AsyncMock(return_value=MOCK_LLM_RESPONSE)
    monkeypatch.setattr(
        "app.services.parsing_service.parse_code_with_llm", mock_parse
    )

    # Create a dummy code and code_version
    test_code = Code(name="test_code")
    db_session.add(test_code)
    await db_session.commit()
    await db_session.refresh(test_code)

    assert isinstance(test_code.id, int)
    test_code_version = CodeVersion(
        code_id=test_code.id, version=1, content="print('hello')"
    )
    db_session.add(test_code_version)
    await db_session.commit()
    await db_session.refresh(test_code_version)

    assert isinstance(test_code_version.id, int)
    test_code_version_id = test_code_version.id

    result_create = ParsingResultCreate(name="Test Parsing Result")

    # 2. Act: Call the service function
    parsing_result = await parsing_service.create_parsing_result(
        db=db_session,
        code_version_id=test_code_version_id,
        result_create=result_create,
    )

    # 3. Assert: Check if the data was created correctly
    assert parsing_result is not None
    assert parsing_result.name == "Test Parsing Result"
    assert parsing_result.code_version_id == test_code_version_id

    # Verify that the LLM mock was called
    mock_parse.assert_called_once_with("print('hello')")

    # Check the content of the created parsing result version
    # Since the relationship is loaded, we can access versions directly.
    await db_session.refresh(parsing_result, ["versions"])
    assert len(parsing_result.versions) == 1
    assert parsing_result.versions[0].content == MOCK_LLM_RESPONSE
    assert parsing_result.versions[0].version == 1
