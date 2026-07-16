import logging
import os
from pathlib import Path
from threading import Lock
from typing import Any

import tensorflow as tf

from config import settings
from utils import load_json

logger = logging.getLogger(__name__)


class ModelLoader:
    def __init__(self) -> None:
        self._model: Any | None = None
        self._classes: list[str] = []
        self._lock = Lock()

    @property
    def model(self) -> Any:
        if self._model is None:
            raise RuntimeError("Model has not been loaded.")
        return self._model

    @property
    def classes(self) -> list[str]:
        if not self._classes:
            raise RuntimeError("Class names have not been loaded.")
        return self._classes

    @property
    def is_loaded(self) -> bool:
        return self._model is not None and bool(self._classes)

    def load(self) -> None:
        with self._lock:
            if self.is_loaded:
                return

            self._validate_files()
            self._classes = self._load_classes()

            logger.info("Loading Keras model from %s", settings.model_path)
            self._model = self._load_keras_model(settings.model_path)
            output_shape = getattr(self._model, "output_shape", None)
            logger.info("Model loaded successfully. Output shape: %s", output_shape)

            if output_shape and output_shape[-1] != len(self._classes):
                raise RuntimeError(
                    f"Model output classes ({output_shape[-1]}) do not match "
                    f"classes.json ({len(self._classes)})."
                )

    def _validate_files(self) -> None:
        if not settings.model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {settings.model_path}. "
                "Place best_model.keras in the project root."
            )
        if settings.model_path.suffix != ".keras":
            raise ValueError("Deployment requires the native Keras .keras model file.")
        if not settings.classes_path.exists():
            raise FileNotFoundError(f"Class names file not found: {settings.classes_path}")

    def _load_classes(self) -> list[str]:
        classes = load_json(settings.classes_path)
        if not isinstance(classes, list) or not all(isinstance(item, str) for item in classes):
            raise ValueError("classes.json must contain a JSON list of class-name strings.")
        return classes

    def _load_keras_model(self, model_path: Path) -> Any:
        original_cwd = Path.cwd()
        try:
            os.chdir(model_path.parent)
            return tf.keras.models.load_model("best_model.keras", compile=False)
        finally:
            os.chdir(original_cwd)


model_loader = ModelLoader()
