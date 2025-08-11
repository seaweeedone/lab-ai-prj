### 개발 작업 목록: Kind 클러스터 관리 API

**1단계: 프로젝트 초기 설정 및 환경 구성**

*   [ ] 1.1. 프로젝트 디렉토리 생성 (`kind-api`)
*   [ ] 1.2. Python 가상 환경 생성 및 활성화 (`python -m venv venv`)
*   [ ] 1.3. FastAPI 및 Uvicorn 설치 (`pip install fastapi uvicorn[standard]`)
*   [ ] 1.4. 기본 프로젝트 구조 생성
    *   `main.py`: FastAPI 앱 초기화 및 라우터 포함
    *   `api/`: 엔드포인트 라우터 모듈 디렉토리
        *   `api/clusters.py`: 클러스터 관련 API 엔드포인트
    *   `services/`: 비즈니스 로직 (kind 명령어 실행) 디렉토리
        *   `services/kind_service.py`: `kind` 명령어 실행 및 관리 로직
    *   `models/`: Pydantic 데이터 모델 디렉토리
        *   `models/cluster.py`: API 요청/응답 데이터 모델
*   [ ] 1.5. `requirements.txt` 파일 생성 (`pip freeze > requirements.txt`)

**2단계: 핵심 로직 개발 (`services/kind_service.py`)**

*   [ ] 2.1. `kind get clusters` 명령어 실행 함수 구현
*   [ ] 2.2. `kind create cluster` 명령어 비동기 실행 함수 구현
    *   Python의 `asyncio.create_subprocess_shell`을 사용하여 비동기 처리
    *   클러스터 이름, 노드 버전, 설정(config)을 인자로 받도록 구현
*   [ ] 2.3. `kind delete cluster` 명령어 실행 함수 구현
*   [ ] 2.4. 명령어 실행 중 발생할 수 있는 오류 처리 (e.g., `subprocess` 오류)

**3단계: API 엔드포인트 구현 (`api/clusters.py`)**

*   [ ] 3.1. Pydantic 모델 정의 (`models/cluster.py`)
    *   `ClusterCreateRequest`: 클러스터 생성 요청 모델 (`cluster_name`, `node_version` 등)
    *   `ClusterResponse`: 클러스터 정보 응답 모델
    *   `TaskResponse`: 비동기 작업 응답 모델 (`task_id`, `status`)
*   [ ] 3.2. 클러스터 생성 API 구현 (`POST /clusters`)
    *   FastAPI의 `BackgroundTasks`를 사용하여 클러스터 생성을 백그라운드 작업으로 처리
    *   작업 ID를 생성하고 즉시 `202 Accepted` 상태와 함께 작업 ID 반환
*   [ ] 3.3. 클러스터 목록 조회 API 구현 (`GET /clusters`)
*   [ ] 3.4. 클러스터 삭제 API 구현 (`DELETE /clusters/{cluster_name}`)
*   [ ] 3.5. (심화) 작업 상태 조회 API 구현 (`GET /tasks/{task_id}`)
    *   간단한 인메모리 딕셔너리를 사용하여 작업 상태 (대기, 진행중, 완료, 실패) 저장 및 조회

**4단계: 테스트 및 문서화**

*   [ ] 4.1. `pytest` 및 `httpx` 설치 (`pip install pytest httpx`)
*   [ ] 4.2. 단위 테스트 작성
    *   `services/kind_service.py`의 각 함수에 대한 단위 테스트 (kind 명령어 실행은 Mocking 처리)
*   [ ] 4.3. 통합 테스트 작성
    *   FastAPI의 `TestClient`를 사용하여 각 API 엔드포인트 테스트
*   [ ] 4.4. `README.md` 파일 작성
    *   프로젝트 설명, 설치 방법, 실행 방법 (`uvicorn main:app --reload`)
    *   API 사용 예시 (`curl` 명령어) 포함

**5단계: 최종 검토 및 리팩토링**

*   [ ] 5.1. 코드 전체 리뷰 및 클린 코드 원칙에 따른 리팩토링
*   [ ] 5.2. 오류 처리 로직 강화 (e.g., 존재하지 않는 클러스터 삭제 시 404 반환)
*   [ ] 5.3. FastAPI 자동 생성 문서 (Swagger UI) 확인 및 정보 보강
