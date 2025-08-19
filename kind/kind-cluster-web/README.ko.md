# Kind 클러스터 관리 웹 서비스

이 프로젝트는 `kind`로 생성된 쿠버네티스 클러스터를 관리하고 모니터링하기 위한 Next.js 기반 웹 애플리케이션입니다.

## 기능

- **클러스터 관리**:
  - 기존 `kind` 클러스터 목록을 표시합니다.
  - 선택적 노드 버전 및 사용자 정의 구성을 사용하여 새 `kind` 클러스터를 생성합니다.
  - `kind` 클러스터를 삭제합니다.
  - 비동기 클러스터 생성 작업의 상태를 추적합니다.
- **클러스터 리소스 모니터링**:
  - 선택한 클러스터의 세부 정보(노드 수, 파드 요약, 서비스 수, 배포 수)를 봅니다.
  - 선택한 클러스터 내의 다양한 쿠버네티스 리소스(노드, 파드, 서비스, 배포)를 나열합니다.
  - YAML 정의를 포함하여 개별 리소스에 대한 자세한 정보를 봅니다.
  - 파드에 대한 실시간 로그를 스트리밍합니다.

## 시작하기

먼저, 이 프론트엔드 애플리케이션은 백엔드 API(`kind-api`)에 의존하므로 백엔드 API가 실행 중인지 확인하십시오.

개발 서버를 실행하려면:

```bash
npm install
npm run dev
```

브라우저에서 [http://localhost:3000](http://localhost:3000)을 열어 결과를 확인하십시오.

## 프로젝트 구조

```
kind-cluster-web/
├── public/               # 정적 자산
├── src/
│   ├── app/              # Next.js 앱 라우터 페이지 및 레이아웃
│   │   ├── clusters/     # 클러스터 세부 정보 및 리소스에 대한 동적 라우트
│   │   │   ├── [clusterName]/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [resourceType]/
│   │   │   │       ├── page.tsx
│   │   │   │       └── [resourceName]/
│   │   │   │           ├── page.tsx
│   │   │   │           └── logs/
│   │   │   │               └── page.tsx # 파드 로그 스트리밍
│   │   ├── favicon.ico
│   │   ├── globals.css
│   │   ├── layout.tsx    # 애플리케이션의 루트 레이아웃
│   │   └── page.tsx      # 홈 페이지 (클러스터 목록)
│   ├── components/       # 재사용 가능한 React 컴포넌트
│   │   ├── CreateClusterModal.tsx
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── YamlView.tsx
│   ├── hooks/            # 사용자 정의 React 훅 (예: Zustand 스토어)
│   │   └── useClusterStore.ts
│   ├── lib/              # 유틸리티 함수 및 구성
│   │   └── axios.ts      # API 호출을 위한 Axios 인스턴스
│   ├── theme/            # Material-UI 테마 구성
│   │   └── theme.ts
│   └── types/            # TypeScript 타입 정의
│       └── cluster.ts
├── .gitignore
├── next.config.ts
├── package.json
├── tsconfig.json
└── ...
```

## 사용된 기술

- [Next.js](https://nextjs.org/)
- [React](https://react.dev/)
- [Material-UI (MUI)](https://mui.com/)
- 데이터 페칭을 위한 [SWR](https://swr.vercel.app/)
- [Zustand](https://zustand-bear.github.io/)
- [Axios](https://axios-http.com/)
- YAML 파싱/문자열화를 위한 [YAML](https://eemeli.org/yaml/)

## 더 알아보기

Next.js에 대해 더 자세히 알아보려면 다음 리소스를 참조하십시오:

- [Next.js 문서](https://nextjs.org/docs) - Next.js 기능 및 API에 대해 알아봅니다.
- [Next.js 배우기](https://nextjs.org/learn) - 대화형 Next.js 튜토리얼입니다.

[Next.js GitHub 리포지토리](https://github.com/vercel/next.js)를 확인해 볼 수 있습니다. 여러분의 피드백과 기여를 환영합니다!

## Vercel에 배포

Next.js 앱을 배포하는 가장 쉬운 방법은 Next.js 개발자가 만든 [Vercel 플랫폼](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme)을 사용하는 것입니다.

자세한 내용은 [Next.js 배포 문서](https://nextjs.org/docs/app/building-your-application/deploying)를 참조하십시오.
