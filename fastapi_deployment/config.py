from pathlib import Path
from typing import Final


BASE_DIR: Final[Path] = Path(__file__).resolve().parent
PROJECT_ROOT: Final[Path] = BASE_DIR.parent


class Settings:
    app_name: str = "Oral Disease Classification API"
    app_version: str = "1.0.0"
    model_filename: str = "best_model.keras"
    model_path: Path = PROJECT_ROOT / model_filename
    classes_path: Path = BASE_DIR / "classes.json"
    image_size: tuple[int, int] = (224, 224)
    color_mode: str = "rgb"
    max_upload_mb: int = 10
    allowed_content_types: frozenset[str] = frozenset(
        {
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/bmp",
            "image/tiff",
        }
    )
    required_dirs: tuple[Path, ...] = (
        BASE_DIR / "uploads",
        BASE_DIR / "responses",
        BASE_DIR / "models",
        BASE_DIR / "logs",
    )
    log_file: Path = BASE_DIR / "logs" / "app.log"


settings = Settings()
