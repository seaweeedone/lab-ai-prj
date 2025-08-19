# Kind Cluster Management Web Service

This project is a Next.js-based web application for managing and monitoring Kubernetes clusters created with `kind`.

## Features

- **Cluster Management**:
  - List existing `kind` clusters.
  - Create new `kind` clusters with optional node versions and custom configurations.
  - Delete `kind` clusters.
  - Track the status of asynchronous cluster creation tasks.
- **Cluster Resource Monitoring**:
  - View details of a selected cluster (node count, pod summary, service count, deployment count).
  - List various Kubernetes resources (Nodes, Pods, Services, Deployments) within a selected cluster.
  - View detailed information for individual resources, including their YAML definitions.
  - Stream real-time logs for pods.

## Getting Started

First, ensure you have the backend API (`kind-api`) running, as this frontend application relies on it.

To run the development server:

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Project Structure

```
kind-cluster-web/
├── public/               # Static assets
├── src/
│   ├── app/              # Next.js App Router pages and layouts
│   │   ├── clusters/     # Dynamic routes for cluster details and resources
│   │   │   ├── [clusterName]/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [resourceType]/
│   │   │   │       ├── page.tsx
│   │   │   │       └── [resourceName]/
│   │   │   │           ├── page.tsx
│   │   │   │           └── logs/
│   │   │   │               └── page.tsx # Pod logs streaming
│   │   ├── favicon.ico
│   │   ├── globals.css
│   │   ├── layout.tsx    # Root layout for the application
│   │   └── page.tsx      # Home page (cluster listing)
│   ├── components/       # Reusable React components
│   │   ├── CreateClusterModal.tsx
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── YamlView.tsx
│   ├── hooks/            # Custom React hooks (e.g., Zustand store)
│   │   └── useClusterStore.ts
│   ├── lib/              # Utility functions and configurations
│   │   └── axios.ts      # Axios instance for API calls
│   ├── theme/            # Material-UI theme configuration
│   │   └── theme.ts
│   └── types/            # TypeScript type definitions
│       └── cluster.ts
├── .gitignore
├── next.config.ts
├── package.json
├── tsconfig.json
└── ...
```

## Technologies Used

- [Next.js](https://nextjs.org/)
- [React](https://react.dev/)
- [Material-UI (MUI)](https://mui.com/)
- [SWR](https://swr.vercel.app/) for data fetching
- [Zustand](https://zustand-bear.github.io/)
- [Axios](https://axios-http.com/)
- [YAML](https://eemeli.org/yaml/) for YAML parsing/stringifying

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

YouYou can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
