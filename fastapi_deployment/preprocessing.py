from io import BytesIO

import numpy as np
from PIL import Image, UnidentifiedImageError
from fastapi import HTTPException, UploadFile, status

from config import settings


def validate_upload(file: UploadFile, content: bytes) -> None:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a filename.",
        )

    if file.content_type not in settings.allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported image type: {file.content_type}",
        )

    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded image is empty.",
        )

    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Uploaded image exceeds {settings.max_upload_mb} MB.",
        )


def preprocess_image(content: bytes) -> np.ndarray:
    """Match the notebook: RGB load_img, target_size=(224,224), img_to_array, expand dims."""
    try:
        with Image.open(BytesIO(content)) as image:
            image = image.convert("RGB")
            image = image.resize(settings.image_size, Image.Resampling.NEAREST)
            image_array = np.asarray(image, dtype=np.float32)
    except UnidentifiedImageError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is not a valid image.",
        ) from exc

    return np.expand_dims(image_array, axis=0)
