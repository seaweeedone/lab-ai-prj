export interface Cluster {
  name: string;
}

export interface ClusterCreateRequest {
  cluster_name: string;
  node_version?: string;
  num_workers?: number;
  config?: string;
}

export interface TaskResponse {
  message: string;
  task_id: string;
}

export interface ClusterDeleteResponse {
  message: string;
}

export interface PodSummary {
  running: number;
  succeeded: number;
  pending: number;
  failed: number;
}

export interface ClusterDetailsResponse {
  node_count: number;
  pod_summary: PodSummary;
  service_count: number;
  deployment_count: number;
}
