from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import code_router, code_version_router, parsing_router

app = FastAPI(
    title="Katib Code Parsing API",
    description="API for parsing ML code and managing related data for Katib.",
    version="0.1.0",
)

origins = [
    "http://localhost",
    "http://localhost:3000",  # React development server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(code_router.router, prefix="/codes", tags=["codes"])
app.include_router(
    code_version_router.router,
    prefix="/codes/{code_id}/versions",
    tags=["code_versions"],
)
app.include_router(parsing_router.router, prefix="/parsing", tags=["parsing"])


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Welcome to the Katib Code Parsing API"}
