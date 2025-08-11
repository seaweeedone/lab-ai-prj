
import asyncio
import logging
import shlex

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_command(command: str) -> tuple[str, str, int]:
    """Executes a shell command and returns its stdout, stderr, and return code."""
    # The command is now expected to be pre-quoted where necessary
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    stdout_str = stdout.decode().strip()
    stderr_str = stderr.decode().strip()
    
    if process.returncode != 0:
        logger.error(f"Command failed: {command}")
        logger.error(f"Stderr: {stderr_str}")

    return stdout_str, stderr_str, process.returncode

async def get_clusters() -> list[str]:
    """Retrieves a list of all kind clusters."""
    # This command has no user input, so it's safe.
    stdout, _, returncode = await run_command("kind get clusters")
    if returncode == 0 and stdout:
        return stdout.splitlines()
    return []

async def create_cluster(cluster_name: str, node_version: str | None = None, num_workers: int | None = None, config_path: str | None = None):
    """Creates a new kind cluster asynchronously, with shell injection protection."""
    safe_cluster_name = shlex.quote(cluster_name)
    cmd = f"kind create cluster --name {safe_cluster_name}"

    if config_path:
        safe_config_path = shlex.quote(config_path)
        cmd += f" --config {safe_config_path}"
    else:
        # Generate a default config if no config_path is provided
        config_lines = [
            "kind: Cluster",
            "apiVersion: kind.x-k8s.io/v1alpha4",
            "nodes:",
            "- role: control-plane"
        ]
        if num_workers is not None and num_workers > 0:
            for _ in range(num_workers):
                config_lines.append("- role: worker")
        
        generated_config_content = "\n".join(config_lines)
        
        # Create a temporary file for the generated kind config
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".yaml") as tmp_file:
            tmp_file.write(generated_config_content)
            config_path = tmp_file.name
        cmd += f" --config {shlex.quote(config_path)}"

    if node_version:
        safe_node_version = shlex.quote(node_version)
        cmd += f" --image kindest/node:v{safe_node_version}"

    logger.info(f"Starting cluster creation for '{cluster_name}' with command: {cmd}")
    stdout, stderr, returncode = await run_command(cmd)
    if returncode == 0:
        logger.info(f"Successfully created cluster '{cluster_name}'.")
    else:
        logger.error(f"Failed to create cluster '{cluster_name}'. Stderr: {stderr}")
    
    # Clean up the temporary config file if it was generated
    if 'generated_config_content' in locals() and config_path and os.path.exists(config_path):
        os.remove(config_path)

async def delete_cluster(cluster_name: str) -> bool:
    """Deletes a kind cluster, with shell injection protection."""
    safe_cluster_name = shlex.quote(cluster_name)
    cmd = f"kind delete cluster --name {safe_cluster_name}"
    
    logger.info(f"Deleting cluster '{cluster_name}'...")
    _, _, returncode = await run_command(cmd)
    if returncode == 0:
        logger.info(f"Successfully deleted cluster '{cluster_name}'.")
        return True
    else:
        logger.error(f"Failed to delete cluster '{cluster_name}'.")
        return False

async def run_kubectl_command(cluster_name: str, command: str) -> tuple[str, str, int]:
    """Runs a kubectl command against a specific cluster context."""
    # Security: Whitelist allowed commands
    allowed_commands = ["get", "describe", "logs"]
    command_parts = shlex.split(command)
    if not command_parts or command_parts[0] not in allowed_commands:
        raise ValueError(f"Disallowed kubectl command: {command_parts[0]}")

    # Set the context for the command
    safe_cluster_name = shlex.quote(cluster_name)
    context_cmd = f"kubectl config use-context kind-{safe_cluster_name}"
    _, stderr, returncode = await run_command(context_cmd)
    if returncode != 0:
        raise RuntimeError(f"Failed to set kubectl context: {stderr}")

    # Force JSON output for 'get' and 'describe' for consistent parsing
    if command_parts[0] in ["get", "describe"] and "-o" not in command_parts:
        command += " -o json"
    
    safe_command = f"kubectl {command}"
    return await run_command(safe_command)

