# 상세 기능 및 API 명세서

## 1. 개요
머신러닝 코드를 관리하고, LLM을 이용하여 코드를 Katib에서 사용 가능한 형태로 파싱하는 시스템의 상세 기능 및 API 명세서이다.

---

## 2. 데이터 모델 (SQLAlchemy & Pydantic)

### 2.1. ORM 모델 (models.py)

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Code(Base):
    __tablename__ = 'codes'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    versions = relationship("CodeVersion", back_populates="code", cascade="all, delete-orphan")

class CodeVersion(Base):
    __tablename__ = 'code_versions'
    id = Column(Integer, primary_key=True, index=True)
    code_id = Column(Integer, ForeignKey('codes.id'), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    code = relationship("Code", back_populates="versions")
    parsing_results = relationship("ParsingResult", back_populates="code_version", cascade="all, delete-orphan")

class ParsingResult(Base):
    __tablename__ = 'parsing_results'
    id = Column(Integer, primary_key=True, index=True)
    code_version_id = Column(Integer, ForeignKey('code_versions.id'), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    code_version = relationship("CodeVersion", back_populates="parsing_results")
    versions = relationship("ParsingResultVersion", back_populates="parsing_result", cascade="all, delete-orphan")

class ParsingResultVersion(Base):
    __tablename__ = 'parsing_result_versions'
    id = Column(Integer, primary_key=True, index=True)
    parsing_result_id = Column(Integer, ForeignKey('parsing_results.id'), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False) # JSON content
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    parsing_result = relationship("ParsingResult", back_populates="versions")
```

### 2.2. Pydantic 스키마 (schemas.py)

```python
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import datetime

# --- Parsing Result Schemas ---
class ParsingResultVersionBase(BaseModel):
    content: Dict[str, Any]

class ParsingResultVersionCreate(ParsingResultVersionBase):
    pass

class ParsingResultVersionInDB(ParsingResultVersionBase):
    id: int
    version: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class ParsingResultBase(BaseModel):
    name: str

class ParsingResultCreate(ParsingResultBase):
    pass

class ParsingResultInDB(ParsingResultBase):
    id: int
    code_version_id: int
    created_at: datetime.datetime
    versions: List[ParsingResultVersionInDB] = []

    class Config:
        orm_mode = True

# --- Code Schemas ---
class CodeVersionBase(BaseModel):
    content: str

class CodeVersionCreate(CodeVersionBase):
    pass

class CodeVersionInDB(CodeVersionBase):
    id: int
    version: int
    created_at: datetime.datetime
    parsing_results: List[ParsingResultInDB] = []

    class Config:
        orm_mode = True

class CodeBase(BaseModel):
    name: str

class CodeCreate(CodeBase):
    content: str

class CodeInDB(CodeBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    versions: List[CodeVersionInDB] = []

    class Config:
        orm_mode = True
```

---

## 3. API 명세

### 3.1. ML 코드 관리 API (`/codes`)

#### `POST /codes`
- **설명:** 새로운 ML 코드를 생성합니다. 첫 번째 버전의 코드가 함께 생성됩니다.
- **Request Body:** `schemas.CodeCreate`
- **Response (201):** `schemas.CodeInDB`

#### `GET /codes`
- **설명:** 모든 ML 코드의 목록을 조회합니다.
- **Response (200):** `List[schemas.CodeInDB]`

#### `GET /codes/{code_id}`
- **설명:** 특정 ML 코드의 상세 정보를 버전 정보와 함께 조회합니다.
- **Response (200):** `schemas.CodeInDB`

#### `PUT /codes/{code_id}`
- **설명:** 특정 ML 코드의 이름을 수정합니다.
- **Request Body:** `schemas.CodeBase`
- **Response (200):** `schemas.CodeInDB`

#### `DELETE /codes/{code_id}`
- **설명:** 특정 ML 코드를 모든 버전과 함께 삭제합니다.
- **Response (204):** No Content

### 3.2. ML 코드 버전 관리 API (`/codes/{code_id}/versions`)

#### `POST /codes/{code_id}/versions`
- **설명:** 특정 ML 코드의 새로운 버전을 생성합니다.
- **Request Body:** `schemas.CodeVersionCreate`
- **Response (201):** `schemas.CodeVersionInDB`

#### `DELETE /codes/{code_id}/versions/{version_id}`
- **설명:** 특정 ML 코드의 특정 버전을 삭제합니다.
- **Response (204):** No Content

### 3.3. 코드 파싱 API (`/parsing`)

#### `POST /parsing/code-versions/{code_version_id}`
- **설명:** 특정 코드 버전을 LLM을 이용해 파싱하고, 첫 번째 파싱 결과를 생성합니다.
- **Request Body:** `schemas.ParsingResultCreate` (파싱 결과의 초기 이름)
- **Response (201):** `schemas.ParsingResultInDB`

#### `GET /parsing/results/{result_id}`
- **설명:** 특정 파싱 결과의 상세 정보를 모든 버전과 함께 조회합니다.
- **Response (200):** `schemas.ParsingResultInDB`

#### `PUT /parsing/results/{result_id}`
- **설명:** 특정 파싱 결과의 이름을 수정합니다.
- **Request Body:** `schemas.ParsingResultBase`
- **Response (200):** `schemas.ParsingResultInDB`

#### `DELETE /parsing/results/{result_id}`
- **설명:** 특정 파싱 결과를 모든 버전과 함께 삭제합니다.
- **Response (204):** No Content

### 3.4. 파싱 결과 버전 관리 API (`/parsing/results/{result_id}/versions`)

#### `POST /parsing/results/{result_id}/versions`
- **설명:** 특정 파싱 결과의 새로운 버전을 생성합니다. (사용자가 파싱 결과를 수동으로 수정하고 저장할 때 사용)
- **Request Body:** `schemas.ParsingResultVersionCreate`
- **Response (201):** `schemas.ParsingResultVersionInDB`

#### `DELETE /parsing/results/{result_id}/versions/{version_id}`
- **설명:** 특정 파싱 결과의 특정 버전을 삭제합니다.
- **Response (204):** No Content

---

## 4. 코드 파싱 로직 (LLM)

- **LLM 기반 파싱:**
    - 코드 상세 페이지 내에서 'Parse' 버튼을 클릭하여 머신러닝 코드를 파싱하는 기능을 제공한다.
    - 파싱은 LLM을 사용하여, 주어진 머신러닝 코드를 논리적 블록으로 나누고 메타데이터를 추출하는 과정이다.
- **파싱 가이드 및 예시:**
    - 파싱 로직은 `examples/Code_Parsing_Guide.pdf` 파일의 가이드를 따른다.
    - `examples/org_code_iris.py` -> `examples/parsing_result_iris.json`
    - `examples/org_code_mnist.py` -> `examples/parsing_result_mnist.json`
- **파싱 입력 (LLM Prompt):**
    - LLM에 전달되는 프롬프트는 다음 구조를 가진다.
    ```
    You are a helpful assistant that parses machine learning code into logical blocks.

    **Instructions:**
    1.  Analyze the provided Python script.
    2.  Identify the machine learning framework used (e.g., "tensorflow", "pytorch", "scikit-learn").
    3.  Extract the names of the metrics used for evaluation (e.g., "accuracy", "loss").
    4.  Isolate the code block responsible for defining the model architecture ("model_block").
    5.  Isolate the code block responsible for command-line argument parsing where hyperparameters are defined ("parameter").
    6.  Isolate the code block responsible for loading data, preprocessing, training, and evaluation ("data_block").
    7.  Format the output as a single JSON object.

    **Python Code:**
    ```python
    {python_code_content}
    ```

    **JSON Output:**
    ```json
    ```
    - `{python_code_content}` 부분에 현재 화면에 표시된 버전의 코드가 삽입된다.
- **파싱 출력 (JSON):**
    - 파싱 결과는 다음 JSON 형식으로 생성된다.
    ```json
    {
      "name": "org_code_iris",
      "framework": "tensorflow",
      "metric": ["accuracy"],
      "parameter": "parser.add_argument('--batch-size', type=int, default=5,...)",
      "model_block": "import ...\n\ndef iris_model():\n    ...",
      "data_block": "def main():\n    parser = argparse.ArgumentParser()..."
    }
    ```