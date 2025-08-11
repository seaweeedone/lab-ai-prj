### 기능: FastAPI를 이용한 Kind Kubernetes 클러스터 관리 API

이 API는 사용자가 HTTP 요청을 통해 Kubernetes 클러스터를 생성하고 관리할 수 있도록 하는 것을 목표로 합니다. WSL(Windows Subsystem for Linux) 환경에서 실행되며, 내부적으로 `kind` 명령어를 사용하여 Docker 컨테이너로 Kubernetes 클러스터를 구축합니다.

**세부 기능 명세:**

1.  **클러스터 생성 (POST /clusters)**
    *   **요청:**
        *   `cluster_name` (필수): 생성할 클러스터의 이름.
        *   `node_version` (선택): Kubernetes 노드의 버전 (예: `1.27.3`). 지정하지 않으면 `kind`의 기본 버전 사용.
        *   `config` (선택): 다중 노드 클러스터 등 복잡한 구성을 위한 `kind` 클러스터 설정 YAML 파일 내용.
    *   **동작:**
        *   요청을 받으면 `kind create cluster` 명령어를 비동기적으로 실행합니다. 클러스터 생성은 시간이 걸릴 수 있으므로, 작업이 시작되었음을 즉시 응답하고 백그라운드에서 생성을 진행합니다.
    *   **성공 응답 (202 Accepted):**
        *   `message`: "클러스터 '{cluster_name}' 생성이 시작되었습니다."
        *   `task_id`: 생성 작업 추적을 위한 고유 ID.

2.  **클러스터 목록 조회 (GET /clusters)**
    *   **동작:** `kind get clusters` 명령어를 실행하여 현재 생성된 클러스터의 목록을 가져옵니다.
    *   **성공 응답 (200 OK):**
        *   현재 존재하는 클러스터 이름의 배열 (예: `["kind", "my-cluster"]`).

3.  **클러스터 삭제 (DELETE /clusters/{cluster_name})**
    *   **동작:** `kind delete cluster --name {cluster_name}` 명령어를 실행하여 특정 클러스터를 삭제합니다.
    *   **성공 응답 (200 OK):**
        *   `message`: "클러스터 '{cluster_name}'가 성공적으로 삭제되었습니다."
    *   **실패 응답 (404 Not Found):**
        *   해당 이름의 클러스터가 존재하지 않을 경우.

4.  **작업 상태 조회 (GET /tasks/{task_id})**
    *   **동작:** 클러스터 생성과 같은 비동기 작업의 현재 상태(대기, 진행 중, 완료, 실패)를 조회합니다.
    *   **성공 응답 (200 OK):**
        *   `status`: "in_progress" | "completed" | "failed"
        *   `result`: 작업 완료 시 결과 메시지.
        *   `error`: 작업 실패 시 에러 메시지.

**기술 스택 및 환경:**

*   **언어/프레임워크:** Python, FastAPI
*   **실행 환경:** WSL2 (Ubuntu 등)
*   **필수 설치 프로그램:**
    *   Docker (WSL2 연동 활성화)
    *   `kind`
    *   `kubectl`
