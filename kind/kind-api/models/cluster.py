
from pydantic import BaseModel, Field
from typing import Optional

class ClusterCreateRequest(BaseModel):
    """Request model for creating a new cluster."""
    cluster_name: str = Field(..., description="The name of the cluster to create.")
    node_version: Optional[str] = Field(None, description="The Kubernetes node image version (e.g., 1.27.3).")
    num_workers: Optional[int] = Field(None, description="The number of worker nodes to create. Defaults to 0.", ge=0)
    config: Optional[str] = Field(None, description="The content of the kind cluster configuration YAML.")

class ClusterResponse(BaseModel):
    """Response model for a single cluster's details."""
    name: str

class TaskResponse(BaseModel):
    """Response model for accepted background tasks."""
    message: str
    task_id: str

class ClusterDeleteResponse(BaseModel):
    """Response model for cluster deletion status."""
    message: str

class PodSummary(BaseModel):
    running: int
    succeeded: int
    pending: int
    failed: int

class ClusterDetailsResponse(BaseModel):
    node_count: int
    pod_summary: PodSummary
    service_count: int
    deployment_count: int

