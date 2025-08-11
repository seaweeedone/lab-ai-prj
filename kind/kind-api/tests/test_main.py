
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import asyncio

from fastapi.testclient import TestClient
# Adjust the path to import the app object
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

client = TestClient(app)

@pytest.fixture
def mock_kind_service():
    """Mocks the kind_service functions to avoid actual shell commands during tests."""
    with patch('api.clusters.kind_service') as mock_service:
        # Mock the async functions
        mock_service.get_clusters = MagicMock(return_value=asyncio.Future())
        mock_service.get_clusters.return_value.set_result(['existing-cluster'])

        mock_service.delete_cluster = MagicMock(return_value=asyncio.Future())
        # We can set different results based on the input in the test itself

        # The create_cluster is called in a background task, so we mock it here
        # to prevent it from actually running.
        mock_service.create_cluster = MagicMock(return_value=asyncio.Future())
        mock_service.create_cluster.return_value.set_result(None)
        
        yield mock_service

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_list_clusters_endpoint(mock_kind_service):
    response = client.get("/api/clusters")
    assert response.status_code == 200
    assert response.json() == [{"name": "existing-cluster"}]
    mock_kind_service.get_clusters.assert_called_once()

def test_create_cluster_endpoint(mock_kind_service):
    # We are not testing the background task runner itself, 
    # but that the endpoint correctly queues the task.
    cluster_data = {"cluster_name": "new-test-cluster"}
    response = client.post("/api/clusters", json=cluster_data)
    
    assert response.status_code == 202 # Accepted
    response_json = response.json()
    assert "task_id" in response_json
    assert response_json["message"] == "Cluster 'new-test-cluster' creation has been queued."

    # You could extend this to check the task status endpoint, but that requires
    # more complex mocking of the background task execution.

def test_delete_cluster_endpoint_success(mock_kind_service):
    # Mock the service to return success
    mock_kind_service.delete_cluster.return_value.set_result(True)
    
    response = client.delete("/api/clusters/existing-cluster")
    assert response.status_code == 200
    assert response.json() == {"message": "Cluster 'existing-cluster' has been deleted successfully."}
    mock_kind_service.delete_cluster.assert_called_once_with("existing-cluster")

def test_delete_cluster_endpoint_not_found(mock_kind_service):
    # Mock the service to return failure (cluster not found)
    mock_kind_service.delete_cluster.return_value.set_result(False)
    
    response = client.delete("/api/clusters/non-existent-cluster")
    assert response.status_code == 404
    assert "detail" in response.json()
    mock_kind_service.delete_cluster.assert_called_once_with("non-existent-cluster")


@patch('api.clusters.kind_service.run_kubectl_command', new_callable=MagicMock)
def test_proxy_kubectl_command_success(mock_run_kubectl):
    # Configure the mock to return a coroutine that resolves to the desired value
    mock_run_kubectl.return_value = asyncio.sleep(0, result=('{"items": []}', '', 0))

    response = client.get("/api/clusters/my-cluster/proxy?command=get pods")

    assert response.status_code == 200
    assert response.json() == {"items": []}


@patch('api.clusters.kind_service.run_kubectl_command', new_callable=MagicMock)
def test_get_cluster_details_success(mock_run_kubectl):
    results = [
        ('{"items": [{"metadata": {}}]}', '', 0),
        ('{"items": [{"status": {"phase": "Running"}}]}', '', 0),
        ('{"items": []}', '', 0),
        ('{"items": [{}, {}]}', '', 0),
    ]
    side_effects = [asyncio.sleep(0, result=res) for res in results]
    mock_run_kubectl.side_effect = side_effects

    response = client.get("/api/clusters/my-cluster/details")

    assert response.status_code == 200
    details = response.json()
    assert details["node_count"] == 1
    assert details["pod_summary"]["running"] == 1


@pytest.mark.parametrize("resource_type, namespace", [
    ("nodes", None),
    ("namespaces", None),
    ("pods", "default"),
    ("services", "kube-system"),
    ("deployments", None),
])
@patch('api.clusters.kind_service.run_kubectl_command', new_callable=MagicMock)
def test_get_resource_endpoints(mock_run_kubectl, resource_type, namespace):
    # Mock the async function
    mock_run_kubectl.return_value = asyncio.sleep(0, result=('{"items": ["test"]}', '', 0))
    
    url = f"/api/clusters/my-cluster/{resource_type}"
    if namespace:
        url += f"?namespace={namespace}"

    response = client.get(url)

    assert response.status_code == 200
    assert response.json() == {"items": ["test"]}

    expected_command = f"get {resource_type}"
    if namespace:
        expected_command += f" -n {namespace}"
    
    # Since we are using an async mock, we need to await the call
    mock_run_kubectl.assert_called_once_with("my-cluster", expected_command)


