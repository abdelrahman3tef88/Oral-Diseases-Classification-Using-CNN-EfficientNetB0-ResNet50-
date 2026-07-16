from pydantic import BaseModel, Field


class RootResponse(BaseModel):
    app_name: str
    version: str
    docs_url: str
    redoc_url: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_path: str
    classes_count: int
    image_size: tuple[int, int]


class PredictionResponse(BaseModel):
    predicted_class: str = Field(..., examples=["Gingivitis"])
    confidence: float = Field(..., examples=[98.45])
    all_predictions: dict[str, float]
