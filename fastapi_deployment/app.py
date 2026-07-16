import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import settings
from model_loader import model_loader
from predict import predict_image
from schemas import HealthResponse, PredictionResponse
from utils import configure_logging, ensure_required_directories

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("Starting %s %s", settings.app_name, settings.app_version)
    ensure_required_directories()
    model_loader.load()
    logger.info("Startup validation completed")
    yield
    logger.info("Shutting down %s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="FastAPI deployment for the trained Oral Disease Classification Keras model.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@app.get("/", response_class=HTMLResponse)
def root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "app_name": settings.app_name,
            "version": settings.app_version,
        },
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="healthy" if model_loader.is_loaded else "not_ready",
        model_loaded=model_loader.is_loaded,
        model_path=str(settings.model_path),
        classes_count=len(model_loader.classes) if model_loader.is_loaded else 0,
        image_size=settings.image_size,
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)) -> PredictionResponse:
    return await predict_image(file)
