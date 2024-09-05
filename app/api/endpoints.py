from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import aiohttp
from PIL import Image
import io
import base64
import asyncio
import os
import uuid
from fastapi import APIRouter, HTTPException, Depends

from app.utils.auth import verify_jwt

from app.models.request_models import ImageProcessingRequest, LoginRequest
from app.services.image_processing import fetch_image, process_image
from app.services.supabase import upload_image_to_supabase
from app.core.config import SUPABASE_BUCKET, SUPABASE_ANON_PUBLIC_KEY, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_URL
from app.services.supabase import supabase

router = APIRouter()


@router.post("/process-image-auth")
async def process_image_endpoint_auth(request: ImageProcessingRequest, user_id: str = Depends(verify_jwt)):
    """Endpoint to process a single image and add it to a background."""
    try:
        # Fetch images from URLs
        image_bytes = await fetch_image(request.image_url)
        background_bytes = await fetch_image(request.background_url)

        # Process the image
        result_image_bytes = await process_image(image_bytes, background_bytes)

        # Save processed image temporarily
        temp_filename = f"{uuid.uuid4()}.png"
        temp_file_path = os.path.join("/tmp", temp_filename)
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(result_image_bytes)

        # Get the filename for the image from the URL
        supabase_filename = f"{user_id}/{request.image_url.split('/')[-1]}_processed_{uuid.uuid4()}.png"

        # Upload to Supabase
        upload_image_to_supabase(SUPABASE_BUCKET, temp_file_path, supabase_filename)

        # Clean up the temporary file
        os.remove(temp_file_path)

        # Return the Supabase URL for the uploaded image
        supabase_image_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{supabase_filename}"
        return {"processed_image_url": supabase_image_url}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    


@router.post("/process-image")
async def process_image_endpoint_auth(request: ImageProcessingRequest):
    """Endpoint to process a single image and add it to a background."""
    try:
        response = supabase.auth.admin.list_users()
        print(response)
        # Fetch images from URLs
        image_bytes = await fetch_image(request.image_url)
        background_bytes = await fetch_image(request.background_url)

        # Process the image
        result_image_bytes = await process_image(image_bytes, background_bytes)

        # Save processed image temporarily
        temp_filename = f"{uuid.uuid4()}.png"
        temp_file_path = os.path.join("/tmp", temp_filename)
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(result_image_bytes)

        # Get the filename for the image from the URL
        supabase_filename = f"other/{request.image_url.split('/')[-1]}_processed_{uuid.uuid4()}.png"

        # Upload to Supabase
        upload_image_to_supabase(SUPABASE_BUCKET, temp_file_path, supabase_filename)

        # Clean up the temporary file
        os.remove(temp_file_path)

        # Return the Supabase URL for the uploaded image
        supabase_image_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{supabase_filename}"
        return {"processed_image_url": supabase_image_url}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    


@router.post("/login")
async def login(request: LoginRequest):
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": request.email, "password": request.password})        
        print(response)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")