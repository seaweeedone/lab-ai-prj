
# Kind Cluster Management Web App Test Plan

This document outlines the test plan for the Kind Cluster Management web application.

## 1. Cluster Management

| Feature | Test Case | Expected Result |
| :--- | :--- | :--- |
| **List Clusters** | 1.1. Navigate to the main page. | 1.1. A list of existing Kind clusters is displayed. |
| | 1.2. Verify that the cluster names are correct. | 1.2. The cluster names match the output of `kind get clusters`. |
| **Create Cluster** | 2.1. Click on the "Create Cluster" button. | 2.1. A modal or a new page appears with a form for creating a new cluster. |
| | 2.2. Enter a valid cluster name and click "Create". | 2.2. The cluster is created successfully, and the new cluster appears in the cluster list. |
| | 2.3. Enter an invalid cluster name (e.g., with special characters) and click "Create". | 2.3. An error message is displayed, and the cluster is not created. |
| | 2.4. Create a cluster with a custom node version. | 2.4. The cluster is created with the specified node version. |
| | 2.5. Create a cluster with a specific number of worker nodes. | 2.5. The cluster is created with the specified number of worker nodes. |
| | 2.6. Create a cluster with a custom configuration file. | 2.6. The cluster is created with the specified configuration. |
| **Delete Cluster** | 3.1. Click on the delete button for a specific cluster. | 3.1. A confirmation dialog appears. |
| | 3.2. Confirm the deletion. | 3.2. The cluster is deleted successfully, and it is removed from the cluster list. |
| | 3.3. Cancel the deletion. | 3.3. The cluster is not deleted. |

## 2. Cluster Details

| Feature | Test Case | Expected Result |
| :--- | :--- | :--- |
| **View Cluster Details** | 4.1. Click on a cluster name in the cluster list. | 4.1. The user is navigated to the cluster details page. |
| | 4.2. Verify that the cluster name is displayed correctly. | 4.2. The correct cluster name is displayed on the page. |
| | 4.3. Verify that the node count, pod summary, service count, and deployment count are displayed correctly. | 4.3. The numbers match the output of the corresponding `kubectl` commands. |

## 3. Resource Management

| Feature | Test Case | Expected Result |
| :--- | :--- | :--- |
| **List Resources** | 5.1. Navigate to the cluster details page. | 5.1. A list of resource types (Nodes, Pods, Services, Deployments) is displayed. |
| | 5.2. Click on a resource type (e.g., "Pods"). | 5.2. The user is navigated to the list of resources of that type. |
| | 5.3. Verify that the list of resources is displayed correctly. | 5.3. The list of resources matches the output of the corresponding `kubectl get` command. |
| | 5.4. For pods, verify that the "All Namespaces" checkbox is checked by default. | 5.4. All pods from all namespaces are displayed. |
| | 5.5. For pods, uncheck the "All Namespaces" checkbox. | 5.5. Only pods from the default namespace are displayed. |
| **View Resource Details** | 6.1. Click on a resource name in the resource list. | 6.1. The user is navigated to the resource details page. |
| | 6.2. Verify that the resource details are displayed correctly. | 6.2. The resource details match the output of the `kubectl describe` command. |
| **View Pod Logs** | 7.1. Navigate to the details page of a running pod. | 7.1. A "Logs" tab or section is available. |
| | 7.2. Click on the "Logs" tab. | 7.2. The logs of the pod are displayed. |
| | 7.3. Verify that the logs are updated in real-time (if the "follow" option is implemented). | 7.3. New log entries appear as they are generated. |
