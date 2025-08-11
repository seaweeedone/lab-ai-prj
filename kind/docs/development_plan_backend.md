### **부록: 백엔드 API 확장 요구사항 명세**

프론트엔드 기능 구현을 위해 `kind-api` 백엔드에 다음 기능들이 추가 또는 확장되어야 합니다.

**1. 범용 `kubectl` 프록시 엔드포인트**

*   **엔드포인트:** `GET /api/clusters/{cluster_name}/proxy`
*   **설명:** 프론트엔드에서 요청하는 `kubectl` 명령어를 지정된 클러스터 컨텍스트에서 안전하게 실행하고, 그 결과를 JSON 형태로 반환합니다. 이 엔드포인트는 리소스 조회 및 상세 정보 확인의 핵심입니다.
*   **요청 (Query Parameters):**
    *   `command` (필수): 실행할 `kubectl` 명령어 문자열 (예: `get pods -A -o json`).
*   **구현 시 고려사항:**
    *   **보안:** 허용할 `kubectl` 명령어와 옵션을 화이트리스트 방식으로 제한하여 예상치 못한 명령어(예: `delete`, `exec`) 실행을 차단해야 합니다. (예: `get`, `describe`, `logs`만 허용)
    *   **출력 포맷 강제:** 명령어에 `-o json` 또는 `-o yaml` 옵션을 강제로 추가하여 항상 구조화된 데이터만 반환하도록 보장해야 합니다.
    *   **컨텍스트 설정:** 명령어 실행 전 `kubectl config use-context kind-{cluster_name}` 명령을 통해 타겟 클러스터를 정확히 지정해야 합니다.
*   **예시 요청:** `GET /api/clusters/my-cluster/proxy?command=get pods -n default -o json`
*   **성공 응답 (200 OK):**
    ```json
    // kubectl get pods -n default -o json의 출력 결과
    {
      "apiVersion": "v1",
      "items": [...]
    }
    ```

**2. 리소스 목록 조회를 위한 특화 엔드포인트 (선택적, 권장)**

범용 프록시 대신, 자주 사용되는 리소스 조회를 위해 명시적인 엔드포인트를 만드는 것이 더 안정적이고 관리하기 좋습니다.

*   **엔드포인트 예시:**
    *   `GET /api/clusters/{cluster_name}/nodes`
    *   `GET /api/clusters/{cluster_name}/namespaces`
    *   `GET /api/clusters/{cluster_name}/pods?namespace={namespace}`
    *   `GET /api/clusters/{cluster_name}/services?namespace={namespace}`
    *   `GET /api/clusters/{cluster_name}/deployments?namespace={namespace}`
*   **동작:** 내부적으로 `kubectl get <resource> -o json` 명령을 실행하고 결과를 반환합니다.

**3. 파드 로그 스트리밍을 위한 엔드포인트**

*   **엔드포인트:** `GET /api/clusters/{cluster_name}/pods/{pod_name}/logs?namespace={namespace}`
*   **설명:** 특정 파드의 로그를 스트리밍 형태로 제공합니다. HTTP Streaming 또는 WebSocket을 사용하여 구현할 수 있습니다.
*   **요청 (Query Parameters):**
    *   `follow` (선택, boolean): `true`로 설정 시, `kubectl logs -f`와 동일하게 새로운 로그를 계속 스트리밍합니다.
    *   `tail` (선택, integer): 마지막 N줄의 로그만 가져옵니다.
*   **구현 방식 제안 (HTTP Streaming):**
    *   FastAPI의 `StreamingResponse`를 사용합니다.
    *   `asyncio.create_subprocess_shell`로 `kubectl logs` 명령을 실행하고, `stdout`을 비동기적으로 읽어 클라이언트에게 실시간으로 전송합니다.
*   **성공 응답 (200 OK):**
    *   `Content-Type: text/plain`
    *   로그 내용이 스트리밍됩니다.

**4. 클러스터 상세 정보 엔드포인트**

*   **엔드포인트:** `GET /api/clusters/{cluster_name}/details`
*   **설명:** 클러스터 대시보드에 필요한 요약 정보를 한 번의 API 호출로 가져오기 위한 엔드포인트입니다.
*   **동작:** 내부적으로 `kubectl get nodes`, `kubectl get pods -A` 등의 명령을 병렬로 실행하고, 결과를 요약하여 반환합니다.
*   **성공 응답 (200 OK):**
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
