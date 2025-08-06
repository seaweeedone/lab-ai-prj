# Katib Code Parsing API

## 프로젝트 목적

> **AI for AI Development**
> 이 프로젝트는 AI를 활용하여 AI 기능 개발을 자동화하고 가속화하는 것을 목표로 하는 "AI for AI Development" 프로젝트입니다. 프로젝트의 모든 코드는 Google의 Gemini-2.5-Pro & Gemini-2.5-Flash 모델을 활용하여 작성 및 관리되었습니다.

이 프로젝트는 ML 코드의 파싱 및 버전 관리를 위한 API 서버와 웹 인터페이스를 제공합니다. 사용자는 웹 UI를 통해 ML 코드를 업로드하고, 해당 코드의 특정 버전을 파싱하여 구조화된 정보를 얻을 수 있습니다. 또한, 파싱된 결과는 LLM(Large Language Model)을 통해 분석되어 코드의 핵심 기능, 입력/출력, 주요 로직 등에 대한 설명을 생성합니다.

## 주요 기능

- **웹 기반 인터페이스**: 사용자가 쉽게 ML 코드를 관리하고 파싱 결과를 확인할 수 있는 프론트엔드 제공
- **ML 코드 관리**: ML 코드 등록, 조회, 수정, 삭제
- **ML 코드 버전 관리**: ML 코드의 버전별 관리 및 조회
- **코드 파싱**: 특정 ML 코드 버전의 파싱 및 구조화된 정보 추출
- **LLM 기반 파싱 결과 분석**: 파싱된 코드 정보를 기반으로 LLM을 활용하여 코드 설명 생성

## 기술 스택

* **Backend**: FastAPI, SQLAlchemy, Alembic, Pydantic
* **Frontend**: React, TypeScript, Bootstrap
* **Database**: SQLite
* **Testing**: Pytest
* **Code Quality**: Ruff, Black, MyPy

## 디렉토리 구조

```
./
├── alembic/                  # Alembic DB 마이그레이션 스크립트
├── app/                      # FastAPI 백엔드 애플리케이션
│   ├── common/               # 공통 유틸리티, 헬퍼 함수 등
│   ├── core/                 # DB 설정, 미들웨어 등 핵심 로직
│   ├── models/               # SQLAlchemy ORM 모델 (데이터베이스 테이블 정의)
│   ├── routers/              # API 엔드포인트 (라우터)
│   ├── schemas/              # Pydantic 스키마 (API 요청/응답 데이터 모델)
│   ├── services/             # 비즈니스 로직 (코드 파싱, LLM 연동 등)
│   ├── __init__.py           # 'app' 디렉토리를 Python 패키지로 인식하도록 함
│   ├── constants.py          # 프로젝트 전역에서 사용되는 상수 정의
│   ├── main.py               # FastAPI 애플리케이션의 메인 진입점
│   └── requirements.txt      # 백엔드 Python 종속성 목록
├── docs/                     # 프로젝트 문서
│   ├── api_spec.md           # API 명세
│   ├── CONTRIBUTING.md       # 기여 가이드라인
│   ├── dev-rules.md          # 개발 규칙
│   ├── development_plan.md   # 개발 계획
│   └── feature_spec.md       # 기능 명세
├── examples/                 # 예제 ML 코드 및 파싱 결과 JSON
├── frontend/                 # React 기반 프론트엔드 애플리케이션
├── ml-codes/                 # 사용자가 업로드하고 파싱할 ML 코드 원본
├── tests/                    # Pytest 기반 백엔드 테스트 코드
├── .gitignore                # Git 버전 관리에서 제외할 파일/디렉토리 목록
├── alembic.ini               # Alembic 설정 파일
├── katib_parser.db           # 로컬 개발용 SQLite 데이터베이스 파일
├── pyproject.toml            # Python 프로젝트 및 도구(Ruff, Black, MyPy) 설정
├── pytest.ini                # Pytest 설정 파일
└── README.md                 # 프로젝트 개요 및 안내 (현재 파일)
```

## 설정 및 실행 방법

### 1. 가상 환경 생성 및 활성화

Python 3.10 버전으로 가상 환경을 생성하고 활성화합니다.

```bash
# Conda 사용 시
conda create -n katib_parser python=3.10
conda activate katib_parser

# venv 사용 시
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 2. 백엔드 설정 및 실행

#### 2.1. 필수 라이브러리 설치

프로젝트 루트 디렉토리에서 다음 명령어를 실행하여 백엔드에 필요한 라이브러리를 설치합니다.

```bash
pip install -r app/requirements.txt
```

#### 2.2. 데이터베이스 마이그레이션

Alembic을 사용하여 데이터베이스 스키마를 최신 상태로 마이그레이션합니다.

```bash
alembic upgrade head
```

#### 2.3. 백엔드 서버 실행

Uvicorn을 사용하여 FastAPI 서버를 실행합니다. `--reload` 옵션은 코드 변경 시 서버를 자동으로 재시작합니다.

```bash
uvicorn app.main:app --reload
```

- API 서버는 `http://127.0.0.1:8000` 에서 실행됩니다.
- API 문서는 `http://127.0.0.1:8000/docs` (Swagger UI) 또는 `http://127.0.0.1:8000/redoc` 에서 확인할 수 있습니다.

### 3. 프론트엔드 설정 및 실행

#### 3.1. 종속성 설치

`frontend` 디렉토리로 이동하여 npm 패키지를 설치합니다.

```bash
cd frontend
npm install
```

#### 3.2. 프론트엔드 개발 서버 실행

React 개발 서버를 시작합니다.

```bash
npm start
```

- 프론트엔드 애플리케이션은 `http://localhost:3000` 에서 실행됩니다.

## 테스트 및 코드 품질

### 백엔드 테스트

Pytest를 사용하여 백엔드 API를 테스트합니다.

```bash
pytest
```

### 코드 품질 검사 (Linting & Formatting)

Ruff, Black, MyPy를 사용하여 코드 스타일을 검사하고 포맷을 지정하며, 타입 힌트를 검증합니다.

```bash
# Python (root directory)
# 코드 스타일 검사
ruff check .

# 코드 포맷팅
ruff format .

# Import 정렬
ruff check . --select I --fix

# 타입 힌트 검사
mypy .
```