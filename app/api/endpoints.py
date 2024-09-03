from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import aiohttp
from PIL import Image
import io
import base64
import asyncio
from fastapi import APIRouter, HTTPException

from app.models.request_models import ImageProcessingRequest
from app.services.image_processing import fetch_image, process_image

router = APIRouter()


@router.post("/process-image")
async def process_image_endpoint(request: ImageProcessingRequest):
    """Endpoint to process a single image and add it to a background."""
    try:
        # Fetch images from URLs
        image_bytes = await fetch_image(request.image_url)
        background_bytes = await fetch_image(request.background_url)

        # Process the image
        result_image_bytes = await process_image(image_bytes, background_bytes)

        # Encode the result to base64 for easy transport as a response
        result_image_b64 = base64.b64encode(result_image_bytes).decode('utf-8')
        return {"processed_image": result_image_b64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
