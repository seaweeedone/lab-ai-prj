# Kind 클러스터 관리 API

## 1. 개요

이 프로젝트는 `kind` (Kubernetes in Docker)를 사용하여 쿠버네티스 클러스터를 관리하기 위한 RESTful API를 제공합니다. Python과 FastAPI로 구축되었으며, `kind`와 Docker에 접근할 수 있는 WSL (Windows Subsystem for Linux) 환경에서 실행되도록 특별히 설계되었습니다.

이 API를 통해 사용자는 쿠버네티스 클러스터를 비동기적으로 생성, 나열 및 삭제할 수 있어 로컬 개발 환경을 쉽게 자동화하고 관리할 수 있습니다.

## 2. 주요 기능

- **클러스터 생성**: 지정된 이름과 선택적 쿠버네티스 버전 또는 구성을 사용하여 새 `kind` 클러스터를 비동기적으로 생성합니다.
- **클러스터 목록 조회**: 기존의 모든 `kind` 클러스터 목록을 가져옵니다.
- **클러스터 삭제**: 이름으로 특정 `kind` 클러스터를 삭제합니다.
- **작업 상태 추적**: 작업 ID를 통해 클러스터 생성과 같은 장기 실행 작업의 상태를 모니터링합니다.
- **대화형 API 문서**: `/docs` 엔드포인트에서 자동으로 생성되고 대화형인 API 문서(Swagger UI)를 사용할 수 있습니다.
- **보안**: 셸 주입 취약점을 방지하기 위해 사용자가 제공한 입력은 `shlex.quote`를 사용하여 안전하게 처리됩니다.

## 3. 프로젝트 구조

```
kind-api/
├── api/
│   ├── __init__.py
│   └── clusters.py       # API 엔드포인트 및 라우트를 정의합니다.
├── models/
│   ├── __init__.py
│   └── cluster.py        # 요청/응답 데이터를 위한 Pydantic 모델입니다.
├── services/
│   ├── __init__.py
│   └── kind_service.py   # `kind` CLI와 상호 작용하는 비즈니스 로직입니다.
├── tests/
│   ├── __init__.py
│   └── test_main.py      # API 엔드포인트에 대한 자동화된 테스트입니다.
├── .gitignore
├── main.py               # 기본 FastAPI 애플리케이션 진입점입니다.
├── requirements.txt      # 프로젝트 종속성입니다.
└── README.md             # 이 파일입니다.
```

## 4. 시스템 요구사항

- WSL2 (Ubuntu 또는 다른 최신 Linux 배포판)
- WSL2 통합이 활성화된 Docker Desktop
- `kind` (v0.11.0 이상 권장)
- Python 3.10+

## 5. 설치 및 설정

1.  **리포지토리 복제:**
    ```bash
    git clone <your-repo-url>
    cd kind-api
    ```

2.  **Python 가상 환경 생성 및 활성화:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **종속성 설치:**
    ```bash
    pip install -r requirements.txt
    ```

## 6. 애플리케이션 실행

API 서버를 시작하려면 가상 환경이 활성화되어 있는지 확인하고 프로젝트 루트(`kind-api`)에서 다음 명령을 실행하십시오.

```bash
uvicorn main:app --reload
```

API는 `http://127.0.0.1:8000`에서 접근할 수 있습니다.

## 7. API 엔드포인트

모든 엔드포인트는 `/api` 접두사 아래에서 사용할 수 있습니다.

### 상태 확인

- **GET /health**
  - **설명**: API가 실행 중인지 확인합니다.
  - **성공 응답 (200 OK)**: `{"status": "ok"}`

### 클러스터 관리

- **POST /api/clusters**
  - **설명**: 새 클러스터 생성을 시작합니다. 이것은 비동기 작업입니다.
  - **요청 본문**:
    ```json
    {
      "cluster_name": "my-cluster",
      "node_version": "1.27.3", // 선택 사항
      "num_workers": 2, // 선택 사항: 워커 노드 수. 기본값은 0입니다.
      "num_workers": 2, // 선택 사항: 워커 노드 수. 기본값은 0입니다.
      "config": "kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker" // 선택 사항
    }
    ```
  - **성공 응답 (202 Accepted)**: 생성 과정을 추적할 작업 ID를 반환합니다.
    ```json
    {
      "message": "클러스터 'my-cluster' 생성이 대기열에 추가되었습니다.",
      "task_id": "some-uuid"
    }
    ```

- **GET /api/clusters**
  - **설명**: 기존의 모든 `kind` 클러스터를 나열합니다.
  - **성공 응답 (200 OK)**:
    ```json
    [
      {"name": "kind"},
      {"name": "my-cluster"}
    ]
    ```

- **DELETE /api/clusters/{cluster_name}**
  - **설명**: 이름으로 클러스터를 삭제합니다.
  - **성공 응답 (200 OK)**:
    ```json
    {"message": "클러스터 'my-cluster'가 성공적으로 삭제되었습니다."}
    ```
  - **오류 응답 (404 Not Found)**: 클러스터가 존재하지 않는 경우.

### Kubernetes 리소스 관리

- **GET /api/clusters/{cluster_name}/proxy**
  - **설명**: 지정된 클러스터에 대해 `kubectl` 명령어를 안전하게 실행하고 결과를 반환합니다.
  - **쿼리 파라미터**:
    - `command` (필수): `kubectl` 명령어 문자열 (예: `get pods -A -o json`).
  - **고려 사항**: 허용된 명령어는 화이트리스트(`get`, `describe`, `logs`)로 지정됩니다. 출력은 JSON 또는 YAML로 강제됩니다.
  - **예시 요청**: `GET /api/clusters/my-cluster/proxy?command=get pods -n default -o json`
  - **성공 응답 (200 OK)**:
    ```json
    {
      "apiVersion": "v1",
      "items": [...]
    }
    ```

- **GET /api/clusters/{cluster_name}/nodes**
- **GET /api/clusters/{cluster_name}/namespaces**
- **GET /api/clusters/{cluster_name}/pods?namespace={namespace}**
- **GET /api/clusters/{cluster_name}/services?namespace={namespace}**
- **GET /api/clusters/{cluster_name}/deployments?namespace={namespace}**
  - **설명**: 클러스터 내 특정 Kubernetes 리소스를 나열하기 위한 특화된 엔드포인트입니다.
  - **동작**: 내부적으로 `kubectl get <resource> -o json` 명령을 실행합니다.

- **GET /api/clusters/{cluster_name}/pods/{pod_name}/logs**
  - **설명**: 특정 파드에서 로그를 스트리밍합니다.
  - **쿼리 파라미터**:
    - `follow` (선택, boolean): `true`로 설정 시, 새로운 로그를 계속 스트리밍합니다 (`kubectl logs -f`).
    - `tail` (선택, integer): 마지막 N줄의 로그만 가져옵니다.
  - **성공 응답 (200 OK)**: `Content-Type: text/plain` (로그 내용이 스트리밍됩니다).

- **GET /api/clusters/{cluster_name}/details**
  - **설명**: 클러스터 대시보드에 필요한 집계된 요약 정보를 검색합니다.
  - **동작**: 내부적으로 `kubectl get nodes`, `kubectl get pods -A` 등의 명령을 실행하고 요약된 결과를 반환합니다.
  - **성공 응답 (200 OK)**:
    ```json
    {
      "node_count": 3,
      "pod_summary": {
        "running": 15,
        "succeeded": 2,
        "pending": 1,
        "failed": 0
      },
      "service_count": 5,
      "deployment_count": 4
    }
    ```

### 작업 추적

- **GET /api/tasks/{task_id}**
  - **설명**: 백그라운드 작업(예: 클러스터 생성)의 상태를 검색합니다.
  - **성공 응답 (200 OK)**:
    ```json
    {
      "status": "completed", // queued, in_progress, completed, or failed
      "result": "클러스터 'my-cluster'가 성공적으로 생성되었습니다."
    }
    ```

## 8. 테스트 실행

자동화된 테스트를 실행하려면 가상 환경이 활성화되어 있는지 확인하고 프로젝트 루트에서 `pytest`를 실행하십시오.

```bash
pytest
```

## 9. 기술 참고사항

- **비동기 작업**: 클러스터 생성은 FastAPI의 `BackgroundTasks`를 사용하여 백그라운드에서 처리됩니다. 이는 API가 장기 실행 셸 명령어에서 차단되는 것을 방지합니다.
- **작업 상태**: 백그라운드 작업의 상태는 인메모리 딕셔너리에 저장됩니다. **참고**: 이것은 데모용이며 서버가 다시 시작되면 재설정됩니다. 프로덕션 환경에서는 Redis 또는 Celery와 같은 영구적이고 공유된 작업 큐를 사용하는 것이 좋습니다.

<br>

## 10. Kind로 쿠버네티스 배포하기

이 섹션에서는 이 API를 통해 `kind`를 사용하여 쿠버네티스 클러스터를 배포하는 방법을 설명합니다.

### 전제 조건

- WSL 환경에 `kind`가 설치되어 있고 접근 가능한지 확인하십시오.
- API가 실행 중이어야 합니다 (`uvicorn main:app --reload`).

### 단계

1.  **클러스터 생성:**
    - `/api/clusters` 엔드포인트로 `POST` 요청을 보냅니다.
    - `cluster_name`을 지정할 수 있습니다. 특정 쿠버네티스 버전을 원하면 `node_version`도 포함할 수 있습니다.
    - **`curl` 사용 예시:**
      ```bash
      curl -X POST "http://127.0.0.1:8000/api/clusters" \
      -H "Content-Type: application/json" \
      -d '{
        "cluster_name": "my-first-cluster"
      }'
      ```
    - API는 `task_id`를 반환합니다.

2.  **생성 상태 확인:**
    - 이전 단계의 `task_id`를 사용하여 클러스터 생성을 모니터링합니다.
    - `/api/tasks/{task_id}`로 `GET` 요청을 보냅니다.
    - **`curl` 사용 예시:**
      ```bash
      curl http://127.0.0.1:8000/api/tasks/your-task-id
      ```
    - 상태는 `queued`에서 `in_progress`로, 최종적으로 `completed` 또는 `failed`로 변경됩니다.

3.  **클러스터 확인:**
    - 작업이 `completed`되면 클러스터가 실행 중인지 확인할 수 있습니다.
    - API를 사용하여 모든 `kind` 클러스터를 나열합니다:
      ```bash
      curl http://127.0.0.1:8000/api/clusters
      ```
    - 또는 `kind` CLI를 직접 사용합니다:
      ```bash
      kind get clusters
      ```

4.  **`kubectl` 컨텍스트 설정:**
    - `kind`는 새 클러스터를 사용하도록 `kubectl`을 자동으로 구성합니다. 다음 명령으로 현재 컨텍스트를 확인할 수 있습니다:
      ```bash
      kubectl config current-context
      ```
    - `kind-my-first-cluster`로 설정되어야 합니다.

5.  **클러스터 삭제:**
    - 정리하려면 API를 사용하여 클러스터를 삭제할 수 있습니다.
    - `/api/clusters/{cluster_name}`으로 `DELETE` 요청을 보냅니다.
    - **`curl` 사용 예시:**
      ```bash
      curl -X DELETE http://127.0.0.1:8000/api/clusters/my-first-cluster
      ```

이 워크플로우를 통해 로컬 쿠버네티스 클러스터의 전체 수명 주기를 프로그래밍 방식으로 관리할 수 있습니다.
