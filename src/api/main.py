"""FastAPI application for SimCopilot — Abaqus .inp AI analysis."""
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from ..config.settings import Settings
from ..llm.client import LLMClient
from ..parser.abaqus_parser import parse_sections
from ..services.validator import validate_simulation

# Load settings (includes .env loading)
settings = Settings()

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_settings.project_name,
        description="AI-assisted Abaqus .inp file analysis",
        version=settings.app_settings.project_version,
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
            # Use default file from samples/simple_beam.inp
            try:
                with open("samples/simple_beam.inp", "r", encoding="utf-8") as f:
                    inp_text = f.read()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to load default .inp file: {e}")

        simulation = parse_sections(inp_text)
        issues = validate_simulation(simulation)
        llm_client = LLMClient(settings)  # Uses settings internally
        explanation = llm_client.explain(simulation)

        return JSONResponse({
            "simulation": simulation,
            "validation_issues": issues,
            "explanation": explanation,
        })

    return app

