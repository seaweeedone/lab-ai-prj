import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from unittest.mock import AsyncMock
from pytest import MonkeyPatch

from app.main import app
from app.models import Base, CodeVersion

# In-memory SQLite database for testing
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncSession:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncClient:
    from app.core.database import get_db
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_create_code(client: AsyncClient) -> None:
    code_data = {
        "name": "test_code_create",
        "content": "print('hello world')"
    }
    response = await client.post("/codes/", json=code_data)
    assert response.status_code == 201
    assert response.json()["name"] == "test_code_create"
    assert "id" in response.json()
    assert len(response.json()["versions"]) == 1
    assert response.json()["versions"][0]["content"] == "print('hello world')"

    # Verify it exists in the list
    response = await client.get("/codes/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "test_code_create"


@pytest.mark.asyncio
async def test_get_code(client: AsyncClient) -> None:
    code_data = {
        "name": "test_get_code",
        "content": "print('get code test')"
    }
    create_response = await client.post("/codes/", json=code_data)
    code_id = create_response.json()["id"]

    response = await client.get(f"/codes/{code_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "test_get_code"
    assert response.json()["id"] == code_id
    assert len(response.json()["versions"]) == 1
    assert response.json()["versions"][0]["content"] == "print('get code test')"

    # Test for non-existent code
    response = await client.get("/codes/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_code(client: AsyncClient) -> None:
    code_data = {
        "name": "code_to_update",
        "content": "print('original content')"
    }
    create_response = await client.post("/codes/", json=code_data)
    code_id = create_response.json()["id"]

    update_data = {"name": "updated_code_name"}
    response = await client.put(f"/codes/{code_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == "updated_code_name"
    assert response.json()["id"] == code_id

    # Verify the update by fetching the code
    response = await client.get(f"/codes/{code_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "updated_code_name"

    # Test for non-existent code
    response = await client.put("/codes/999", json=update_data)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_code_version(client: AsyncClient) -> None:
    code_data = {
        "name": "code_for_version",
        "content": "print('version 1')"
    }
    create_response = await client.post("/codes/", json=code_data)
    code_id = create_response.json()["id"]

    version_data = {"content": "print('version 2')"}
    response = await client.post(f"/codes/{code_id}/versions/", json=version_data)
    assert response.status_code == 201
    assert response.json()["version"] == 2
    assert response.json()["content"] == "print('version 2')"

    # Verify the new version is associated with the code
    response = await client.get(f"/codes/{code_id}")
    assert response.status_code == 200
    assert len(response.json()["versions"]) == 2
    assert response.json()["versions"][1]["content"] == "print('version 2')"

    # Test for non-existent code
    response = await client.post("/codes/999/versions/", json=version_data)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_parse_code_version(client: AsyncClient, monkeypatch: MonkeyPatch) -> None:
    # Mock the LLM service function
    MOCK_LLM_RESPONSE = {
        "name": "parsed_test_code",
        "framework": "tensorflow",
        "metric": ["accuracy"],
        "parameter": "--batch-size",
        "model_block": "model = tf.keras.Sequential()",
        "data_block": "(x_train, y_train)",
    }
    mock_parse = AsyncMock(return_value=MOCK_LLM_RESPONSE)
    monkeypatch.setattr(
        "app.services.parsing_service.parse_code_with_llm", mock_parse
    )

    code_data = {
        "name": "code_to_parse",
        "content": "print('code content for parsing')"
    }
    create_code_response = await client.post("/codes/", json=code_data)
    code_id = create_code_response.json()["id"]
    code_version_id = create_code_response.json()["versions"][0]["id"]

    parsing_data = {"name": "Initial Parsing Result"}
    response = await client.post(f"/parsing/code-versions/{code_version_id}", json=parsing_data)
    assert response.status_code == 201
    assert response.json()["name"] == "Initial Parsing Result"
    assert "id" in response.json()
    assert len(response.json()["versions"]) == 1
    assert response.json()["versions"][0]["content"] == MOCK_LLM_RESPONSE

    # Verify LLM mock was called
    mock_parse.assert_called_once_with("print('code content for parsing')")

    # Test for non-existent code version
    response = await client.post("/parsing/code-versions/999", json=parsing_data)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_parsing_result(client: AsyncClient, monkeypatch: MonkeyPatch) -> None:
    # Mock the LLM service function
    MOCK_LLM_RESPONSE = {
        "name": "parsed_test_code",
        "framework": "tensorflow",
        "metric": ["accuracy"],
        "parameter": "--batch-size",
        "model_block": "model = tf.keras.Sequential()",
        "data_block": "(x_train, y_train)",
    }
    mock_parse = AsyncMock(return_value=MOCK_LLM_RESPONSE)
    monkeypatch.setattr(
        "app.services.parsing_service.parse_code_with_llm", mock_parse
    )

    code_data = {
        "name": "code_for_parsing_result",
        "content": "print('code content for parsing result')"
    }
    create_code_response = await client.post("/codes/", json=code_data)
    code_version_id = create_code_response.json()["versions"][0]["id"]

    parsing_data = {"name": "Test Parsing Result"}
    create_parsing_response = await client.post(f"/parsing/code-versions/{code_version_id}", json=parsing_data)
    parsing_result_id = create_parsing_response.json()["id"]

    response = await client.get(f"/parsing/results/{parsing_result_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Parsing Result"
    assert response.json()["id"] == parsing_result_id
    assert len(response.json()["versions"]) == 1
    assert response.json()["versions"][0]["content"] == MOCK_LLM_RESPONSE

    # Test for non-existent parsing result
    response = await client.get("/parsing/results/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_parsing_result(client: AsyncClient, monkeypatch: MonkeyPatch) -> None:
    # Mock the LLM service function
    MOCK_LLM_RESPONSE = {
        "name": "parsed_test_code",
        "framework": "tensorflow",
        "metric": ["accuracy"],
        "parameter": "--batch-size",
        "model_block": "model = tf.keras.Sequential()",
        "data_block": "(x_train, y_train)",
    }
    mock_parse = AsyncMock(return_value=MOCK_LLM_RESPONSE)
    monkeypatch.setattr(
        "app.services.parsing_service.parse_code_with_llm", mock_parse
    )

    code_data = {
        "name": "code_for_update_parsing_result",
        "content": "print('code content for update parsing result')"
    }
    create_code_response = await client.post("/codes/", json=code_data)
    code_version_id = create_code_response.json()["versions"][0]["id"]

    parsing_data = {"name": "Original Parsing Result Name"}
    create_parsing_response = await client.post(f"/parsing/code-versions/{code_version_id}", json=parsing_data)
    parsing_result_id = create_parsing_response.json()["id"]

    update_data = {"name": "Updated Parsing Result Name"}
    response = await client.put(f"/parsing/results/{parsing_result_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Parsing Result Name"
    assert response.json()["id"] == parsing_result_id

    # Verify the update by fetching the parsing result
    response = await client.get(f"/parsing/results/{parsing_result_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Parsing Result Name"

    # Test for non-existent parsing result
    response = await client.put("/parsing/results/999", json=update_data)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_parsing_result_version(client: AsyncClient, monkeypatch: MonkeyPatch) -> None:
    # Mock the LLM service function
    MOCK_LLM_RESPONSE = {
        "name": "parsed_test_code",
        "framework": "tensorflow",
        "metric": ["accuracy"],
        "parameter": "--batch-size",
        "model_block": "model = tf.keras.Sequential()",
        "data_block": "(x_train, y_train)",
    }
    mock_parse = AsyncMock(return_value=MOCK_LLM_RESPONSE)
    monkeypatch.setattr(
        "app.services.parsing_service.parse_code_with_llm", mock_parse
    )

    code_data = {
        "name": "code_for_parsing_result_version",
        "content": "print('code content for parsing result version')"
    }
    create_code_response = await client.post("/codes/", json=code_data)
    code_version_id = create_code_response.json()["versions"][0]["id"]

    parsing_data = {"name": "Original Parsing Result"}
    create_parsing_response = await client.post(f"/parsing/code-versions/{code_version_id}", json=parsing_data)
    parsing_result_id = create_parsing_response.json()["id"]

    new_content = {"new_key": "new_value"}
    version_data = {"content": new_content}
    response = await client.post(f"/parsing/results/{parsing_result_id}/versions", json=version_data)
    assert response.status_code == 201
    assert response.json()["version"] == 2
    assert response.json()["content"] == new_content

    # Verify the new version is associated with the parsing result
    response = await client.get(f"/parsing/results/{parsing_result_id}")
    assert response.status_code == 200
    assert len(response.json()["versions"]) == 2
    assert response.json()["versions"][1]["content"] == new_content

    # Test for non-existent parsing result
    response = await client.post("/parsing/results/999/versions", json=version_data)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_code_version(client: AsyncClient) -> None:
    code_data = {
        "name": "code_to_delete_version",
        "content": "print('version 1 to delete')"
    }
    create_response = await client.post("/codes/", json=code_data)
    code_id = create_response.json()["id"]
    code_version_id = create_response.json()["versions"][0]["id"]

    # Create another version to ensure it's not the only one
    version_data = {"content": "print('version 2')"}
    await client.post(f"/codes/{code_id}/versions/", json=version_data)

    response = await client.delete(f"/codes/{code_id}/versions/{code_version_id}")
    assert response.status_code == 204

    # Verify the version is deleted
    response = await client.get(f"/codes/{code_id}")
    assert response.status_code == 200
    assert len(response.json()["versions"]) == 1
    assert response.json()["versions"][0]["id"] != code_version_id

    # Test for non-existent code version
    response = await client.delete(f"/codes/{code_id}/versions/999")
    assert response.status_code == 404

    # Test for non-existent code
    response = await client.delete("/codes/999/versions/1")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_parsing_result_version(client: AsyncClient, monkeypatch: MonkeyPatch) -> None:
    # Mock the LLM service function
    MOCK_LLM_RESPONSE = {
        "name": "parsed_test_code",
        "framework": "tensorflow",
        "metric": ["accuracy"],
        "parameter": "--batch-size",
        "model_block": "model = tf.keras.Sequential()",
        "data_block": "(x_train, y_train)",
    }
    mock_parse = AsyncMock(return_value=MOCK_LLM_RESPONSE)
    monkeypatch.setattr(
        "app.services.parsing_service.parse_code_with_llm", mock_parse
    )

    code_data = {
        "name": "code_for_delete_parsing_result_version",
        "content": "print('code content for delete parsing result version')"
    }
    create_code_response = await client.post("/codes/", json=code_data)
    code_version_id = create_code_response.json()["versions"][0]["id"]

    parsing_data = {"name": "Parsing Result to Delete Version"}
    create_parsing_response = await client.post(f"/parsing/code-versions/{code_version_id}", json=parsing_data)
    parsing_result_id = create_parsing_response.json()["id"]
    parsing_result_version_id = create_parsing_response.json()["versions"][0]["id"]

    # Create another version to ensure it's not the only one
    new_content = {"another_key": "another_value"}
    version_data = {"content": new_content}
    await client.post(f"/parsing/results/{parsing_result_id}/versions", json=version_data)

    response = await client.delete(f"/parsing/results/{parsing_result_id}/versions/{parsing_result_version_id}")
    assert response.status_code == 204

    # Verify the version is deleted
    response = await client.get(f"/parsing/results/{parsing_result_id}")
    assert response.status_code == 200
    assert len(response.json()["versions"]) == 1
    assert response.json()["versions"][0]["id"] != parsing_result_version_id

    # Test for non-existent parsing result version
    response = await client.delete(f"/parsing/results/{parsing_result_id}/versions/999")
    assert response.status_code == 404

    # Test for non-existent parsing result
    response = await client.delete("/parsing/results/999/versions/1")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_code(client: AsyncClient) -> None:
    code_data = {
        "name": "code_to_delete",
        "content": "print('code to delete')"
    }
    create_response = await client.post("/codes/", json=code_data)
    code_id = create_response.json()["id"]

    response = await client.delete(f"/codes/{code_id}")
    assert response.status_code == 204

    # Verify the code is deleted
    response = await client.get(f"/codes/{code_id}")
    assert response.status_code == 404

    # Test for non-existent code
    response = await client.delete("/codes/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_parsing_result(client: AsyncClient, monkeypatch: MonkeyPatch) -> None:
    # Mock the LLM service function
    MOCK_LLM_RESPONSE = {
        "name": "parsed_test_code",
        "framework": "tensorflow",
        "metric": ["accuracy"],
        "parameter": "--batch-size",
        "model_block": "model = tf.keras.Sequential()",
        "data_block": "(x_train, y_train)",
    }
    mock_parse = AsyncMock(return_value=MOCK_LLM_RESPONSE)
    monkeypatch.setattr(
        "app.services.parsing_service.parse_code_with_llm", mock_parse
    )

    code_data = {
        "name": "code_for_delete_parsing_result",
        "content": "print('code content for delete parsing result')"
    }
    create_code_response = await client.post("/codes/", json=code_data)
    code_version_id = create_code_response.json()["versions"][0]["id"]

    parsing_data = {"name": "Parsing Result to Delete"}
    create_parsing_response = await client.post(f"/parsing/code-versions/{code_version_id}", json=parsing_data)
    parsing_result_id = create_parsing_response.json()["id"]

    response = await client.delete(f"/parsing/results/{parsing_result_id}")
    assert response.status_code == 204

    # Verify the parsing result is deleted
    response = await client.get(f"/parsing/results/{parsing_result_id}")
    assert response.status_code == 404

    # Test for non-existent parsing result
    response = await client.delete("/parsing/results/999")
    assert response.status_code == 404
