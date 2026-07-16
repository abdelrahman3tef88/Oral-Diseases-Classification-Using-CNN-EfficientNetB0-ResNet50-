import json
import logging
from pathlib import Path
from typing import Any

from config import settings


def ensure_required_directories() -> None:
    for directory in settings.required_dirs:
        directory.mkdir(parents=True, exist_ok=True)


def configure_logging() -> None:
    ensure_required_directories()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(settings.log_file, encoding="utf-8"),
        ],
        force=True,
    )


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Required JSON file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)
