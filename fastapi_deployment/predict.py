import logging

import numpy as np
from fastapi import HTTPException, UploadFile, status

from model_loader import model_loader
from preprocessing import preprocess_image, validate_upload
from schemas import PredictionResponse

logger = logging.getLogger(__name__)


async def predict_image(file: UploadFile) -> PredictionResponse:
    content = await file.read()
    validate_upload(file, content)

    try:
        batch = preprocess_image(content)
        raw_prediction = model_loader.model.predict(batch, verbose=0)
        probabilities = np.asarray(raw_prediction[0], dtype=np.float64)

        predicted_index = int(np.argmax(probabilities))
        confidence = float(np.max(probabilities) * 100.0)
        predicted_class = model_loader.classes[predicted_index]

        all_predictions = {
            class_name: round(float(probability * 100.0), 4)
            for class_name, probability in zip(model_loader.classes, probabilities, strict=True)
        }

        return PredictionResponse(
            predicted_class=predicted_class,
            confidence=round(confidence, 2),
            all_predictions=all_predictions,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Prediction failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {exc}",
        ) from exc
