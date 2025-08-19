# Kind Cluster Management API

## 1. Overview

This project provides a RESTful API for managing Kubernetes clusters using `kind` (Kubernetes in Docker). It is built with Python and FastAPI, and is specifically designed to run within a WSL (Windows Subsystem for Linux) environment where `kind` and Docker are accessible.

The API allows users to create, list, and delete Kubernetes clusters asynchronously, making it easy to automate and manage local development environments.

## 2. Features

- **Create Cluster**: Asynchronously create a new `kind` cluster with a specified name and optional Kubernetes version or configuration.
- **List Clusters**: Get a list of all existing `kind` clusters.
- **Delete Cluster**: Delete a specific `kind` cluster by name.
- **Task Status Tracking**: Monitor the status of long-running operations like cluster creation via a task ID.
- **Interactive API Docs**: Automatically generated and interactive API documentation (Swagger UI) available at the `/docs` endpoint.
- **Security**: User-provided inputs are sanitized using `shlex.quote` to prevent shell injection vulnerabilities.

## 3. Project Structure

```
kind-api/
├── api/
│   ├── __init__.py
│   └── clusters.py       # Defines the API endpoints and routes.
├── models/
│   ├── __init__.py
│   └── cluster.py        # Pydantic models for request/response data.
├── services/
│   ├── __init__.py
│   └── kind_service.py   # Business logic for interacting with the `kind` CLI.
├── tests/
│   ├── __init__.py
│   └── test_main.py      # Automated tests for the API endpoints.
├── .gitignore
├── main.py               # Main FastAPI application entrypoint.
├── requirements.txt      # Project dependencies.
└── README.md             # This file.
```

## 4. System Requirements

- WSL2 (Ubuntu or other modern Linux distribution)
- Docker Desktop with WSL2 integration enabled
- `kind` (v0.11.0 or newer recommended)
- Python 3.10+

## 5. Installation and Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd kind-api
    ```

2.  **Create and activate a Python virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## 6. Running the Application

To start the API server, ensure your virtual environment is activated and run the following command from the project root (`kind-api`):

```bash
uvicorn main:app --reload
```

The API will be accessible at `http://127.0.0.1:8000`.

## 7. API Endpoints

All endpoints are available under the `/api` prefix.

### Health Check

- **GET /health**
  - **Description**: Checks if the API is running.
  - **Success Response (200 OK)**: `{"status": "ok"}`

### Cluster Management

- **POST /api/clusters**
  - **Description**: Initiates the creation of a new cluster. This is an asynchronous operation.
  - **Request Body**:
    ```json
    {
      "cluster_name": "my-cluster",
      "node_version": "1.27.3", // Optional
      "num_workers": 2, // Optional: Number of worker nodes. Defaults to 0.
      "num_workers": 2, // Optional: Number of worker nodes. Defaults to 0.
      "config": "kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker" // Optional
    }
    ```
  - **Success Response (202 Accepted)**: Returns a task ID to track the creation process.
    ```json
    {
      "message": "Cluster 'my-cluster' creation has been queued.",
      "task_id": "some-uuid"
    }
    ```

- **GET /api/clusters**
  - **Description**: Lists all existing `kind` clusters.
  - **Success Response (200 OK)**: 
    ```json
    [
      {"name": "kind"},
      {"name": "my-cluster"}
    ]
    ```

- **DELETE /api/clusters/{cluster_name}**
  - **Description**: Deletes a cluster by name.
  - **Successful Response (200 OK)**:
    ```json
    {"message": "Cluster 'my-cluster' has been deleted successfully."}
    ```
  - **Error Response (404 Not Found)**: If the cluster does not exist.

### Kubernetes Resource Management

- **GET /api/clusters/{cluster_name}/proxy**
  - **Description**: Safely executes `kubectl` commands against the specified cluster and returns the results.
  - **Query Parameters**:
    - `command` (required): The `kubectl` command string (e.g., `get pods -A -o json`).
  - **Considerations**: Commands are whitelisted (`get`, `describe`, `logs`). Output is forced to JSON or YAML.
  - **Example Request**: `GET /api/clusters/my-cluster/proxy?command=get pods -n default -o json`
  - **Successful Response (200 OK)**:
    ```json
    {
      "apiVersion": "v1",
      "items": [...]
    }
    ```

- **GET /api/clusters/{cluster_name}/nodes**
- **GET /api/clusters/{cluster_name}/namespaces**
- **GET /api/clusters/{cluster_name}/pods?namespace={namespace}**
- **GET /api/clusters/{cluster_name}/services?namespace={namespace}**
- **GET /api/clusters/{cluster_name}/deployments?namespace={namespace}**
  - **Description**: Specialized endpoints to list specific Kubernetes resources within a cluster.
  - **Operation**: Internally executes `kubectl get <resource> -o json`.

- **GET /api/clusters/{cluster_name}/pods/{pod_name}/logs**
  - **Description**: Streams logs from a specific pod.
  - **Query Parameters**:
    - `follow` (optional, boolean): If `true`, streams new logs continuously (`kubectl logs -f`).
    - `tail` (optional, integer): Retrieves only the last N lines of logs.
  - **Successful Response (200 OK)**: `Content-Type: text/plain` (log content streamed).

- **GET /api/clusters/{cluster_name}/details**
  - **Description**: Retrieves aggregated summary information for a cluster dashboard.
  - **Operation**: Internally executes `kubectl get nodes`, `kubectl get pods -A`, etc., and returns a summarized result.
  - **Successful Response (200 OK)**:
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

### Task Tracking

### Task Tracking

- **GET /api/tasks/{task_id}**
  - **Description**: Retrieves the status of a background task (e.g., cluster creation).
  - **Success Response (200 OK)**:
    ```json
    {
      "status": "completed", // queued, in_progress, completed, or failed
      "result": "Cluster 'my-cluster' created successfully."
    }
    ```

## 8. Running Tests

To run the automated tests, ensure your virtual environment is activated and run `pytest` from the project root:

```bash
pytest
```

## 9. Technical Notes

- **Asynchronous Operations**: Cluster creation is handled in the background using FastAPI's `BackgroundTasks`. This prevents the API from blocking on long-running shell commands.
- **Task State**: The status of background tasks is stored in an in-memory dictionary. **Note**: This is for demonstration purposes only and will be reset if the server restarts. For production use, a persistent and shared task queue like Redis or Celery is recommended.