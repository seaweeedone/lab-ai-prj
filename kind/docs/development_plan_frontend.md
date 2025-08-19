### **개발 작업 목록: Kind 클러스터 관리 웹 서비스 (Next.js)**

**1단계: 프로젝트 초기 설정 및 기본 레이아웃 구성**

*   [ ] 1.1. Next.js 프로젝트 생성 (`npx create-next-app@latest --typescript`)
*   [ ] 1.2. 필수 라이브러리 설치
    *   UI 라이브러리: `npm install @mui/material @emotion/react @emotion/styled`
    *   데이터 페칭: `npm install swr`
    *   상태 관리: `npm install zustand`
    *   API 통신: `npm install axios`
*   [ ] 1.3. 프로젝트 폴더 구조 설정 (`components`, `hooks`, `lib`, `types` 등)
*   [ ] 1.4. 기본 레이아웃 컴포넌트 구현
    *   사이드 네비게이션 바 (메뉴: 클러스터, 노드, 파드 등)
    *   상단 헤더
    *   메인 컨텐츠 영역
*   [ ] 1.5. 테마 및 전역 스타일 설정 (MUI ThemeProvider, global.css)

**2단계: 클러스터 관리 기능 구현**

*   [ ] 2.1. 클러스터 목록 페이지 구현 (`/`)
    *   `useSWR` 훅을 사용하여 `/api/clusters` API 호출 및 데이터 표시
    *   클러스터 목록을 테이블 또는 카드 형태로 렌더링
    *   데이터 로딩 및 오류 상태 처리
*   [ ] 2.2. 클러스터 생성 기능 구현
    *   '새 클러스터 생성' 버튼 및 모달(Dialog) 컴포넌트 생성
    *   클러스터 이름, 버전, 워커 수, YAML 설정을 입력받는 폼 구현
    *   폼 제출 시 `/api/clusters`로 `POST` 요청 전송
*   [ ] 2.3. 클러스터 삭제 기능 구현
    *   삭제 버튼 클릭 시 확인(Confirm) 모달 표시
    *   확인 시 `/api/clusters/{cluster_name}`으로 `DELETE` 요청 전송
*   [ ] 2.4. 비동기 작업 상태 추적 UI 구현
    *   클러스터 생성 요청 후, `useSWR`의 `refreshInterval` 옵션을 사용하여 `/api/tasks/{task_id}`를 주기적으로 폴링
    *   진행 상태를 사용자에게 토스트 메시지나 상태 텍스트로 알림

**3단계: 클러스터 리소스 모니터링 구현 (백엔드 확장 의존)**

*   [ ] 3.1. **(백엔드 작업 선행)** `kubectl` 프록시 API 엔드포인트 구현 필요
*   [ ] 3.2. 클러스터 선택 기능 구현 (Zustand 스토어에 현재 선택된 클러스터 이름 저장)
*   [ ] 3.3. 동적 라우팅 설정 (`/clusters/[clusterName]/[resourceType]`)
*   [ ] 3.4. 리소스 목록 페이지 구현 (Pods, Nodes, Services, Deployments)
    *   `[resourceType]`에 따라 동적으로 `kubectl get {resourceType}` 명령을 백엔드 프록시 API로 요청
    *   결과 데이터를 테이블 형태로 표시하는 공용 컴포넌트 개발
    *   파드 목록의 경우, 네임스페이스 필터링 드롭다운 메뉴 구현

**4단계: 리소스 상세 정보 및 관리 기능 구현**

*   [ ] 4.1. 리소스 상세 정보 페이지 동적 라우팅 (`/clusters/[clusterName]/pods/[podName]`)
*   [ ] 4.2. 상세 정보 표시 UI 구현
    *   `kubectl describe`와 유사한 정보를 표시하는 섹션
    *   `kubectl get ... -o yaml` 결과를 보여주는 YAML 뷰 탭 (Syntax highlighting 라이브러리 사용)
*   [ ] 4.3. 파드 로그 조회 기능 구현
    *   'Logs' 탭 내에서 백엔드 API를 통해 실시간 로그 스트리밍
    *   (고급) WebSocket을 사용하거나, `useSWR`로 주기적 폴링
    *   자동 스크롤 및 로그 다운로드 버튼 구현

**5단계: 테스트 및 최종 검토**

*   [ ] 5.1. 주요 컴포넌트 및 페이지에 대한 단위/통합 테스트 작성 (Jest, React Testing Library)
*   [ ] 5.2. E2E(End-to-End) 테스트 시나리오 작성 및 실행 (Cypress 또는 Playwright)
    *   시나리오: 클러스터 생성 -> 파드 목록 확인 -> 로그 확인 -> 클러스터 삭제
*   [ ] 5.3. 코드 리뷰 및 리팩토링 (성능 최적화, 코드 일관성 유지)
*   [ ] 5.4. 프론트엔드 프로젝트 `README.md` 파일 작성 (설치, 실행, 테스트 방법 명시)

---

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
