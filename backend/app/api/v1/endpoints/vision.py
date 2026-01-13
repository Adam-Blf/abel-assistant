"""
===============================================================================
VISION.PY - Vision API Endpoints
===============================================================================
A.B.E.L. Project - Image Analysis and Understanding
===============================================================================
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.security.auth import get_current_user, get_optional_user
from app.services.gemini.vision import get_vision_service
from app.services.memory import get_rag_pipeline

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/vision", tags=["Vision"])

# Allowed image formats
ALLOWED_IMAGE_TYPES = [
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/heic",
    "image/heif",
]

MAX_IMAGE_SIZE = 20 * 1024 * 1024  # 20 MB


@router.post("/analyze")
@limiter.limit("5/minute")
async def analyze_image(
    request: Request,
    image: UploadFile = File(..., description="Image to analyze"),
    question: Optional[str] = Form(default=None, description="Question about the image"),
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    Analyze an image and describe its contents.

    Optionally answer a specific question about the image.
    Supports: JPEG, PNG, WebP, GIF, HEIC
    Max size: 20MB
    """
    # Validate file type
    content_type = image.content_type or "image/jpeg"
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Format image non supporté: {content_type}",
        )

    # Read and validate size
    image_data = await image.read()
    if len(image_data) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image trop volumineuse (max 20MB)",
        )

    try:
        vision_service = get_vision_service()
        result = await vision_service.analyze_image(
            image_data=image_data,
            mime_type=content_type,
            question=question,
        )

        # Learn from interaction if authenticated and there's a question
        if current_user and question:
            try:
                rag = get_rag_pipeline()
                await rag.extract_and_store_learnings(
                    user_id=current_user["id"],
                    user_message=f"[Image Question] {question}",
                    assistant_response=result.get("description", ""),
                )
            except Exception:
                pass  # Non-blocking

        return {
            "description": result.get("description", ""),
            "has_text": result.get("has_text", False),
            "question": question,
            "image_size": len(image_data),
            "format": content_type,
        }

    except Exception as e:
        logger.error(f"[Vision API] Analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de l'analyse de l'image",
        )


@router.post("/ocr")
@limiter.limit("10/minute")
async def extract_text(
    request: Request,
    image: UploadFile = File(..., description="Image containing text"),
    current_user: dict = Depends(get_current_user),
):
    """
    Extract text from an image (OCR).

    Useful for documents, signs, screenshots, etc.
    """
    # Validate file type
    content_type = image.content_type or "image/jpeg"
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Format image non supporté: {content_type}",
        )

    image_data = await image.read()
    if len(image_data) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image trop volumineuse (max 20MB)",
        )

    try:
        vision_service = get_vision_service()
        result = await vision_service.extract_text(
            image_data=image_data,
            mime_type=content_type,
        )

        return {
            "text": result.get("text", ""),
            "has_text": result.get("has_text", False),
            "image_size": len(image_data),
        }

    except Exception as e:
        logger.error(f"[Vision API] OCR error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de l'extraction du texte",
        )


@router.post("/objects")
@limiter.limit("5/minute")
async def identify_objects(
    request: Request,
    image: UploadFile = File(..., description="Image to analyze"),
    current_user: dict = Depends(get_current_user),
):
    """
    Identify objects in an image.

    Returns a list of detected objects with categories.
    """
    # Validate file type
    content_type = image.content_type or "image/jpeg"
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Format image non supporté: {content_type}",
        )

    image_data = await image.read()
    if len(image_data) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image trop volumineuse (max 20MB)",
        )

    try:
        vision_service = get_vision_service()
        objects = await vision_service.identify_objects(
            image_data=image_data,
            mime_type=content_type,
        )

        return {
            "objects": objects,
            "count": len(objects),
            "image_size": len(image_data),
        }

    except Exception as e:
        logger.error(f"[Vision API] Object detection error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de l'identification des objets",
        )


@router.post("/compare")
@limiter.limit("3/minute")
async def compare_images(
    request: Request,
    image1: UploadFile = File(..., description="First image"),
    image2: UploadFile = File(..., description="Second image"),
    current_user: dict = Depends(get_current_user),
):
    """
    Compare two images and describe differences.

    Useful for before/after comparisons, finding changes, etc.
    """
    # Validate both images
    for img, name in [(image1, "image1"), (image2, "image2")]:
        content_type = img.content_type or "image/jpeg"
        if content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=415,
                detail=f"Format {name} non supporté: {content_type}",
            )

    # Read images
    image1_data = await image1.read()
    image2_data = await image2.read()

    total_size = len(image1_data) + len(image2_data)
    if total_size > MAX_IMAGE_SIZE * 2:
        raise HTTPException(
            status_code=413,
            detail="Images trop volumineuses (max 40MB total)",
        )

    try:
        vision_service = get_vision_service()
        result = await vision_service.compare_images(
            image1_data=image1_data,
            image2_data=image2_data,
            mime_type=image1.content_type or "image/jpeg",
        )

        return {
            "comparison": result.get("comparison", ""),
            "images_analyzed": 2,
        }

    except Exception as e:
        logger.error(f"[Vision API] Comparison error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la comparaison des images",
        )
