
import uuid
import tempfile
import os
import logging
import uuid
import tempfile
import os
import logging
import json
from fastapi import APIRouter, BackgroundTasks, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from typing import List


logger = logging.getLogger(__name__)

from services import kind_service
from models.cluster import (
    ClusterCreateRequest,
    ClusterResponse,
    TaskResponse,
    ClusterDeleteResponse,
    ClusterDetailsResponse,
    PodSummary
)

router = APIRouter()

# A simple in-memory dictionary to store task statuses.
# WARNING: This is for demonstration purposes only. In a production environment,
# this will not work reliably as it is not persistent and not shared across
# multiple server processes or workers. Use a robust solution like Redis or Celery instead.
tasks = {}

def run_cluster_creation(task_id: str, cluster_name: str, node_version: str | None, num_workers: int | None, config_content: str | None):
    """Task runner for cluster creation, designed to be used with BackgroundTasks."""
    tasks[task_id] = {"status": "in_progress", "result": None}
    config_path = None
    if config_content:
        # Create a temporary file for the kind config
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".yaml") as tmp_file:
            tmp_file.write(config_content)
            config_path = tmp_file.name
    
    try:
        import asyncio
        asyncio.run(kind_service.create_cluster(cluster_name, node_version, num_workers, config_path))
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result"] = f"Cluster '{cluster_name}' created successfully."
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["result"] = f"Error creating cluster: {str(e)}"
        logger.error(f"Error in run_cluster_creation for task {task_id}: {e}", exc_info=True)
    finally:
        if config_path and os.path.exists(config_path):
            os.remove(config_path)

@router.post("/clusters", status_code=status.HTTP_202_ACCEPTED, response_model=TaskResponse)
async def create_cluster_endpoint(request: ClusterCreateRequest, background_tasks: BackgroundTasks):
    """Initiates the creation of a new Kubernetes cluster using kind."""
    task_id = str(uuid.uuid4())
    background_tasks.add_task(
        run_cluster_creation, 
        task_id, 
        request.cluster_name, 
        request.node_version, 
        request.num_workers, 
        request.config
    )
    tasks[task_id] = {"status": "queued", "result": None}
    return TaskResponse(message=f"Cluster '{request.cluster_name}' creation has been queued.", task_id=task_id)

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Retrieves the status of a background task."""
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/clusters", response_model=List[ClusterResponse])
async def list_clusters_endpoint():
    """Lists all existing kind clusters."""
    cluster_names = await kind_service.get_clusters()
    return [ClusterResponse(name=name) for name in cluster_names]

@router.delete("/clusters/{cluster_name}", response_model=ClusterDeleteResponse)
async def delete_cluster_endpoint(cluster_name: str):
    """Deletes a specific kind cluster by name."""
    success = await kind_service.delete_cluster(cluster_name)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Cluster '{cluster_name}' not found or could not be deleted."
        )
    return ClusterDeleteResponse(message=f"Cluster '{cluster_name}' has been deleted successfully.")

@router.get("/clusters/{cluster_name}/proxy")
async def proxy_kubectl_command(cluster_name: str, command: str):
    """Proxies a kubectl command to the specified cluster."""
    try:
        stdout, stderr, returncode = await kind_service.run_kubectl_command(cluster_name, command)
        if returncode != 0:
            raise HTTPException(status_code=400, detail=f"Kubectl command failed: {stderr}")
        
        # Try to parse JSON, otherwise return plain text
        try:
            return Response(content=stdout, media_type="application/json")
        except json.JSONDecodeError:
            return Response(content=stdout, media_type="text/plain")

    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clusters/{cluster_name}/details", response_model=ClusterDetailsResponse)
async def get_cluster_details(cluster_name: str):
    """Retrieves aggregated details about a specific cluster."""
    try:
        # Get nodes
        nodes_raw, _, retcode = await kind_service.run_kubectl_command(cluster_name, "get nodes")
        if retcode != 0:
            raise HTTPException(status_code=500, detail="Failed to get nodes")
        nodes = json.loads(nodes_raw)
        node_count = len(nodes.get("items", []))

        # Get pods
        pods_raw, _, retcode = await kind_service.run_kubectl_command(cluster_name, "get pods -A")
        if retcode != 0:
            raise HTTPException(status_code=500, detail="Failed to get pods")
        pods = json.loads(pods_raw)
        pod_summary = PodSummary(running=0, succeeded=0, pending=0, failed=0)
        for pod in pods.get("items", []):
            status = pod.get("status", {}).get("phase", "").lower()
            if status == "running":
                pod_summary.running += 1
            elif status == "succeeded":
                pod_summary.succeeded += 1
            elif status == "pending":
                pod_summary.pending += 1
            elif status == "failed":
                pod_summary.failed += 1

        # Get services
        services_raw, _, retcode = await kind_service.run_kubectl_command(cluster_name, "get services -A")
        if retcode != 0:
            raise HTTPException(status_code=500, detail="Failed to get services")
        services = json.loads(services_raw)
        service_count = len(services.get("items", []))

        # Get deployments
        deployments_raw, _, retcode = await kind_service.run_kubectl_command(cluster_name, "get deployments -A")
        if retcode != 0:
            raise HTTPException(status_code=500, detail="Failed to get deployments")
        deployments = json.loads(deployments_raw)
        deployment_count = len(deployments.get("items", []))

        return ClusterDetailsResponse(
            node_count=node_count,
            pod_summary=pod_summary,
            service_count=service_count,
            deployment_count=deployment_count
        )

    except (RuntimeError, ValueError) as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clusters/{cluster_name}/pods/{pod_name}/logs")
async def stream_pod_logs(cluster_name: str, pod_name: str, namespace: str = "default", follow: bool = False, tail: int = -1):
    """Streams logs from a specific pod."""
    async def log_generator():
        command = f"logs {pod_name} -n {namespace}"
        if follow:
            command += " -f"
        if tail > 0:
            command += f" --tail={tail}"
        
        process = await asyncio.create_subprocess_shell(
            f'kubectl --context kind-{cluster_name} {command}',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        while True:
            line = await process.stdout.readline()
            if not line:
                break
            yield line

    return StreamingResponse(log_generator(), media_type="text/plain")


# Helper for specialized resource endpoints
async def get_resource(cluster_name: str, resource_type: str, all_namespaces: bool = False):
    command = f"get {resource_type}"
    if all_namespaces:
        command += " -A"
    
    try:
        stdout, stderr, returncode = await kind_service.run_kubectl_command(cluster_name, command)
        if returncode != 0:
            raise HTTPException(status_code=400, detail=f"Kubectl command failed: {stderr}")
        return Response(content=stdout, media_type="application/json")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clusters/{cluster_name}/nodes")
async def get_nodes(cluster_name: str):
    return await get_resource(cluster_name, "nodes")

@router.get("/clusters/{cluster_name}/namespaces")
async def get_namespaces(cluster_name: str):
    return await get_resource(cluster_name, "namespaces")

@router.get("/clusters/{cluster_name}/pods")
async def get_pods(cluster_name: str, all_namespaces: bool = False):
    return await get_resource(cluster_name, "pods", all_namespaces)

@router.get("/clusters/{cluster_name}/services")
async def get_services(cluster_name: str, namespace: str | None = None):
    return await get_resource(cluster_name, "services", namespace)

@router.get("/clusters/{cluster_name}/deployments")
async def get_deployments(cluster_name: str, namespace: str | None = None):
    return await get_resource(cluster_name, "deployments", namespace)
