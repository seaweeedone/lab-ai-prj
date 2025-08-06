# 개발 계획 및 작업 목록 (To-Do List)

이 문서는 `feature_spec.md`, `api_spec.md`, `dev-rules.md`를 기반으로 프로젝트 개발을 위한 구체적인 작업 목록을 정의합니다.

---

### Phase 1: 프로젝트 초기 설정

- [ ] **Conda 가상 환경 생성**
  - `conda create -n katib_parser python=3.10`
  - `conda activate katib_parser`
- [ ] **필수 라이브러리 설치**
  - `pip install fastapi uvicorn sqlalchemy alembic python-multipart pydantic[email] ruff black mypy pytest httpx`
- [ ] **`requirements.txt` 파일 생성**
  - `pip freeze > requirements.txt`
- [ ] **기본 프로젝트 디렉토리 구조 생성 (`dev-rules.md` 기반)**
  ```
  ./
  ├── app/
  │   ├── __init__.py
  │   ├── main.py
  │   ├── core/
  │   ├── models/
  │   ├── schemas/
  │   ├── services/
  │   └── routers/
  ├── tests/
  └── alembic/
  ```
- [ ] **FastAPI 앱 초기화 (`app/main.py`)**
  - FastAPI 인스턴스 생성 및 기본 설정

---

### Phase 2: 데이터베이스 설정 및 모델링

- [ ] **데이터베이스 설정 (`app/core/database.py`)**
  - SQLAlchemy 비동기 엔진 및 세션 설정 (로컬 SQLite 사용)
- [ ] **ORM 모델 구현 (`app/models/`)**
  - `api_spec.md`에 정의된 `Code`, `CodeVersion`, `ParsingResult`, `ParsingResultVersion` 모델 작성
- [ ] **Alembic 초기화 및 설정**
  - `alembic init alembic`
  - `alembic/env.py` 파일 수정하여 모델 및 데이터베이스 연결 설정
- [ ] **첫 스키마 마이그레이션 생성 및 적용**
  - `alembic revision --autogenerate -m "Initial schema setup"`
  - `alembic upgrade head`

---

### Phase 3: 백엔드 API 구현

- [x] **Pydantic 스키마 작성 (`app/schemas/`)**
  - `api_spec.md`에 정의된 모든 Pydantic 모델 작성
- [x] **ML 코드 관리 기능 구현 (`codes`)**
  - [x] `services/code_service.py` 작성 (CRUD 비즈니스 로직)
  - [x] `routers/code_router.py` 작성 (API 엔드포인트 정의)
- [x] **ML 코드 버전 관리 기능 구현 (`versions`)**
  - [x] `services/code_version_service.py` 작성
  - [x] `routers/code_version_router.py` 작성
- [x] **코드 파싱 결과 관리 기능 구현 (`parsing_results`)**
  - [x] `services/parsing_service.py` 작성
  - [x] `routers/parsing_router.py` 작성
- [x] **LLM 연동 로직 구현 (`app/services/llm_service.py`)**
  - `feature_spec.md`의 프롬프트 템플릿을 사용하여 LLM에 요청하는 기능 구현
  - `app/common/constants.py`의 `OPENAI_API_KEY`를 참조하여 API 인증 처리
  - 파싱 API (`POST /parsing/code-versions/{code_version_id}`)와 연동
- [x] **FastAPI 라우터 통합 (`app/main.py`)**
  - 생성된 모든 라우터를 메인 앱에 등록

---

### Phase 4: 테스트 및 코드 품질

- [x] **`pytest` 테스트 환경 설정**
- [x] **서비스 로직 단위 테스트 작성 (`tests/`)**
- [x] **API 엔드포인트 통합 테스트 작성 (`tests/`)**
- [ ] **`ruff`, `black`, `mypy` 설정 및 실행**
  - 코드 포맷팅 및 정적 분석을 통한 코드 품질 유지

---

### Phase 5: 문서화

- [x] **`README.md` 작성**
  - `dev-rules.md`의 가이드라인에 따라 프로젝트 목적, 구조, 설정 방법, 실행 방법 등 기술

---

### Phase 6: 프론트엔드 (Vue3) - (별도 진행)

- [x] React 프로젝트 생성
- [x] API 연동을 위한 클라이언트 설정 (Axios)
- [x] 화면별 컴포넌트 개발
  - [x] 코드 목록 조회 페이지
  - [x] 코드 상세 조회 및 수정 페이지
  - [x] 파싱 결과 조회 및 수정 페이지
