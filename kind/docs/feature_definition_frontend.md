### **Kind 클러스터 관리 웹 서비스 - 기능 정의서 (Next.js 기반)**

**1. 프로젝트 개요**

본 프로젝트는 로컬 환경에서 `kind`를 통해 생성된 쿠버네티스 클러스터를 시각적으로 관리하고 모니터링하기 위한 웹 기반 프론트엔드 애플리케이션을 개발하는 것을 목표로 한다. **Next.js** 프레임워크를 사용하여 성능과 개발자 경험을 극대화하고, 기존에 구현된 `kind-api` 백엔드와 연동하여 클러스터의 생명주기를 관리한다. 또한, `kubectl` 명령어를 웹 UI에서 실행하여 클러스터 내부 리소스(노드, 파드, 서비스 등)를 손쉽게 확인하고 관리하는 기능을 제공한다.

**2. 대상 사용자**

*   로컬에서 쿠버네티스 개발 및 테스트 환경을 자주 사용하는 개발자
*   `kubectl` 명령어에 익숙하지만, 시각적인 대시보드를 통해 생산성을 높이고 싶은 DevOps 엔지니어
*   쿠버네티스 클러스터의 구조와 동작을 학습하려는 학생 또는 입문자

**3. 주요 기능 목록 (Features)**

**3.1. 클러스터 관리 (Cluster Management)**
*   **기능:** 백엔드 API와 연동하여 `kind` 클러스터의 생성, 조회, 삭제를 관리한다.
    *   **화면 1: 클러스터 목록 대시보드**
        *   현재 생성된 모든 `kind` 클러스터 목록을 카드 또는 테이블 형태로 표시한다.
        *   각 클러스터의 이름과 상태(예: Running, Creating, Deleting)를 표시한다.
        *   '새 클러스터 생성' 버튼과 각 클러스터별 '관리' 및 '삭제' 버튼을 제공한다.
    *   **화면 2: 클러스터 생성**
        *   '새 클러스터 생성' 버튼 클릭 시 나타나는 모달 또는 별도 페이지.
        *   **입력 필드:**
            *   클러스터 이름 (필수)
            *   쿠버네티스 노드 버전 (선택)
            *   워커 노드 수 (선택)
            *   Kind 설정 YAML (선택, 텍스트 영역으로 제공)
        *   생성 요청 후, 비동기 작업 상태를 UI에 표시 (예: "생성 중..." 토스트 메시지 및 진행률 표시).
    *   **기능 3: 클러스터 삭제**
        *   사용자가 '삭제' 버튼을 누르면, 확인 절차를 거친 후 해당 클러스터를 삭제하는 API를 호출한다.

**3.2. 클러스터 리소스 모니터링 (Cluster Resource Monitoring)**
*   **기능:** 사용자가 특정 클러스터를 선택했을 때, 해당 클러스터 내부의 주요 리소스를 `kubectl`과 유사한 형태로 조회하고 모니터링한다.
    *   **전제 조건:** 이 기능을 위해서는 **백엔드 API에 `kubectl` 명령어를 안전하게 실행하고 그 결과를 JSON 형태로 반환하는 기능 확장이 필요**하다. (예: `GET /api/clusters/{cluster_name}/nodes`)
    *   **화면 4: 클러스터 상세 대시보드**
        *   선택된 클러스터의 개요 정보를 표시 (노드 수, 파드 상태별 개수, 서비스 수 등).
        *   사이드바 또는 탭을 통해 각 리소스(노드, 파드, 서비스, 디플로이먼트 등) 페이지로 이동할 수 있는 네비게이션을 제공한다.
    *   **화면 5: 리소스 목록 조회 (노드, 파드, 서비스, 디플로이먼트 등)**
        *   각 리소스는 테이블 형태로 표시된다.
        *   **파드(Pods) 목록:** 네임스페이스(Namespace) 필터링 기능을 제공한다. (컬럼: Namespace, Name, Status, Restarts, Age, IP)
        *   **노드(Nodes) 목록:** (컬럼: Name, Status, Role, K8s Version, CPU/Memory Usage)
        *   **서비스(Services) 목록:** (컬럼: Namespace, Name, Type, Cluster-IP, Ports, Age)
        *   **디플로이먼트(Deployments) 목록:** (컬럼: Namespace, Name, Ready, Up-to-date, Available, Age)

**3.3. 리소스 상세 조회 및 관리 (Detailed Resource Inspection & Management)**
*   **기능:** 목록에서 특정 리소스를 선택하여 상세 정보를 확인하고, 간단한 관리 작업을 수행한다.
    *   **화면 6: 리소스 상세 정보**
        *   `kubectl describe` 명령어의 출력과 유사한 정보를 표시한다. (Labels, Annotations, Status, Events 등)
        *   YAML 탭을 두어 `kubectl get <resource> <name> -o yaml`의 결과를 보여준다.
    *   **화면 7: 파드 로그(Pod Logs) 조회**
        *   파드 상세 정보 화면 내 'Logs' 탭에서 실시간 로그를 스트리밍하여 보여준다. (`kubectl logs -f <pod-name>`)
        *   로그 다운로드 및 자동 스크롤 활성화/비활성화 기능을 제공한다.

**4. 기술 스택 및 요구사항 (Technology Stack & Requirements)**

*   **프레임워크:** **Next.js (TypeScript)**
    *   서버 사이드 렌더링(SSR)과 정적 사이트 생성(SSG)을 활용하여 초기 로딩 성능을 최적화하고, API 라우트 기능을 통해 프론트엔드와 백엔드(BFF, Backend-for-Frontend) 로직을 통합 관리합니다.

*   **데이터 페칭 및 상태 관리 (Data Fetching & State Management):**
    *   **SWR** 또는 **React Query (TanStack Query):** API로부터 데이터를 가져오고 캐싱, 재검증을 자동화하여 실시간에 가까운 데이터 동기화를 지원합니다. 대시보드 UI에 필수적입니다.
    *   **Zustand** 또는 **Redux Toolkit:** 전역적으로 사용되는 상태(예: 현재 선택된 클러스터, UI 테마 등)를 효율적으로 관리합니다.

*   **UI 라이브러리 및 스타일링:**
    *   **Material-UI (MUI)** 또는 **Ant Design:** 복잡한 데이터 테이블, 모달, 폼 등 엔터프라이즈급 컴포넌트를 빠르게 구축하기 위해 권장됩니다.
    *   **Tailwind CSS:** 커스텀 디자인 시스템을 유연하게 구축하고 일관된 스타일을 유지하는 데 유용합니다.

*   **API 통신:**
    *   Next.js에 내장된 `fetch` API를 기반으로 하며, `SWR` 또는 `React Query`와 함께 사용하여 고도화된 데이터 통신을 구현합니다.

*   **디자인:**
    *   사용자 친화적이고 직관적인 UI/UX.
    *   Next.js의 반응형 디자인 패턴을 적용하여 다양한 화면 크기에서 최적의 경험을 제공합니다.

*   **백엔드 API 요구사항 (Backend API Requirements):**
    *   (기존과 동일) 기존 클러스터 관리 API (`/api/clusters`, `/api/tasks/{task_id}`)
    *   **(신규)** `kubectl` 명령 프록시 엔드포인트:
        *   `GET /api/clusters/{cluster_name}/proxy?command=get%20pods%20-A` 와 같이 `kubectl` 명령을 파라미터로 받아 실행하고 결과를 JSON 형태로 반환하는 보안 강화된 엔드포인트.

**5. 향후 확장 기능 (Future Enhancements)**

*   **리소스 생성/수정:** 웹 UI의 YAML 편집기를 통해 리소스를 직접 생성하거나 수정 (`kubectl apply -f -`).
*   **파드 Exec:** 웹 기반 터미널을 통해 파드 컨테이너에 직접 접속 (`kubectl exec -it <pod-name> -- /bin/sh`).
*   **포트 포워딩 관리:** 특정 서비스나 파드에 대한 포트 포워딩을 UI를 통해 설정하고 관리.
*   **헬름(Helm) 차트 관리:** 클러스터에 설치된 헬름 차트 목록을 조회하고 간단한 릴리스 정보 확인.
