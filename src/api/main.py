"""FastAPI application for SimCopilot — Abaqus .inp AI analysis."""
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from ..config.settings import Settings
from ..llm.client import LLMClient
from ..parser.abaqus_parser import parse_sections
from ..services.geometry import render_mesh_png
from ..services.validator import validate_simulation

# Load settings (includes .env loading)
settings = Settings()

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_settings.project_name,
        description="AI-assisted Abaqus .inp file analysis",
        version=settings.app_settings.project_version,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health():
        return {"status": "ok"}


    @app.post("/explain")
    async def explain(file: UploadFile = None):
        if file is not None:
            if not (file.filename or "").endswith(".inp"):
                raise HTTPException(status_code=400, detail="Only .inp files are supported.")
            content = await file.read()
            try:
                inp_text = content.decode("utf-8")
            except UnicodeDecodeError:
                raise HTTPException(status_code=400, detail="File must be UTF-8 encoded text.")
        else:
            raise HTTPException(status_code=400, detail="No file uploaded.")
        
        simulation = parse_sections(inp_text)
        issues = validate_simulation(simulation)
        llm_client = LLMClient(settings)  # Uses settings internally
        explanation = llm_client.explain(simulation)

        return JSONResponse({
            "simulation": simulation,
            "validation_issues": issues,
            "explanation": explanation,
        })

    @app.post(
        "/visualize",
        response_class=Response,
        responses={200: {"content": {"image/png": {}}, "description": "Mesh wireframe PNG"}},
    )
    async def visualize(file: UploadFile = None):
        """Return a PNG wireframe render of the mesh. No LLM involved."""
        if file is None:
            raise HTTPException(status_code=400, detail="No file uploaded.")
        if not (file.filename or "").endswith(".inp"):
            raise HTTPException(status_code=400, detail="Only .inp files are supported.")
        content = await file.read()
        try:
            inp_text = content.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File must be UTF-8 encoded text.")

        simulation = parse_sections(inp_text)
        try:
            png_bytes = render_mesh_png(simulation)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))

        return Response(content=png_bytes, media_type="image/png")

    return app

