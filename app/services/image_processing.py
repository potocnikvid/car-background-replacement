from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import aiohttp
from PIL import Image
import io
import base64
import asyncio

from app.core.config import API_MODE, API_OPTIONS


async def fetch_image(url: str) -> bytes:
    """Fetch an image from a URL."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise HTTPException(status_code=400, detail=f"Failed to fetch image from {url}")
                return await response.read()
    except aiohttp.ClientError as e:
        # Catching general client errors from aiohttp
        raise HTTPException(status_code=400, detail=f"Client error while fetching image from {url}: {str(e)}")
    except Exception as e:
        # Catching any other unforeseen errors
        raise HTTPException(status_code=500, detail=f"Unexpected error while fetching image from {url}: {str(e)}")


async def process_image(image_bytes: bytes, background_bytes: bytes) -> bytes:
    """Process the image by removing background and adding it to a new background."""
    try:
        async with aiohttp.ClientSession() as session:
            data = {'image': image_bytes}
            async with session.post(API_OPTIONS[API_MODE]['url'],
                                    data=data,
                                    headers=API_OPTIONS[API_MODE]['headers']) as response:
                if response.status != 200:
                    raise HTTPException(status_code=500, detail="Error processing image")
                
                try:
                    resp_json = await response.json()
                except Exception as e:
                    # Handling JSON decoding errors
                    raise HTTPException(status_code=500, detail=f"Error parsing JSON response: {str(e)}")

                # Check if the expected keys exist in the JSON response
                try:
                    img_b64 = resp_json['results'][0]['entities'][0]['image'].encode('utf8')
                except (KeyError, TypeError, AttributeError) as e:
                    # Handling missing keys or wrong response format
                    raise HTTPException(status_code=500, detail=f"Error accessing image data in response: {str(e)}")

        # Decode the base64 image data
        try:
            processed_img_bytes = base64.decodebytes(img_b64)
        except Exception as e:
            # Handling errors during base64 decoding
            raise HTTPException(status_code=500, detail=f"Error decoding base64 image: {str(e)}")

        # Open processed image and background image
        try:
            processed_img = Image.open(io.BytesIO(processed_img_bytes)).convert("RGBA")
            background_img = Image.open(io.BytesIO(background_bytes)).convert("RGBA")
        except Exception as e:
            # Handling errors during image opening or conversion
            raise HTTPException(status_code=500, detail=f"Error opening images: {str(e)}")

        # Resize processed image to fit background if necessary
        try:
            processed_img = processed_img.resize((background_img.width, background_img.height), Image.LANCZOS)
        except Exception as e:
            # Handling errors during image resizing
            raise HTTPException(status_code=500, detail=f"Error resizing processed image: {str(e)}")

        # Paste the processed image onto the background image
        try:
            background_img.paste(processed_img, (0, 0), processed_img)
        except Exception as e:
            # Handling errors during image pasting
            raise HTTPException(status_code=500, detail=f"Error pasting processed image onto background: {str(e)}")

        # Save the final image to a byte stream
        try:
            output_stream = io.BytesIO()
            background_img.save(output_stream, format="PNG")
            output_stream.seek(0)
            return output_stream.read()
        except Exception as e:
            # Handling errors during image saving
            raise HTTPException(status_code=500, detail=f"Error saving final image: {str(e)}")

    except Exception as e:
        # Catching any other unforeseen errors in the process_image function
        raise HTTPException(status_code=500, detail=f"Unexpected error in process_image: {str(e)}")

