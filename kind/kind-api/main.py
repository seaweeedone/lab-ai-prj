
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import clusters

# Configure logging
log_file = "app.log"

# Clear existing handlers to prevent duplicate logs
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
for handler in logging.getLogger("uvicorn").handlers[:]:
    logging.getLogger("uvicorn").removeHandler(handler)
for handler in logging.getLogger("uvicorn.access").handlers[:]:
    logging.getLogger("uvicorn.access").removeHandler(handler)

# Set up file handler
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

# Set up stream handler (console)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, stream_handler]
)

# Ensure uvicorn loggers also write to our handlers
logging.getLogger("uvicorn").handlers = [file_handler, stream_handler]
logging.getLogger("uvicorn.access").handlers = [file_handler, stream_handler]


app = FastAPI(
    title="Kind Cluster Management API",
    description="An API to manage Kubernetes clusters using Kind on WSL.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"], # Allow frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router for cluster management
app.include_router(clusters.router, prefix="/api", tags=["Clusters"])

@app.get("/health", tags=["Health"])
async def health_check():
    """A simple health check endpoint to confirm the API is running."""
    return {"status": "ok"}
