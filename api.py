from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import aiohttp
from PIL import Image
import io
import base64
import asyncio


app = FastAPI()

# Configurations for API4AI
MODE = 'demo'
RESULT_MODE = 'fg-image-shadow'
OPTIONS = {
    'demo': {
        'url': f'https://demo.api4ai.cloud/img-bg-removal/v1/cars/results?mode={RESULT_MODE}',
        'headers': {'A4A-CLIENT-APP-ID': 'sample'}
    }
}


class ImageProcessingRequest(BaseModel):
    image_url: str
    background_url: str


async def fetch_image(url: str) -> bytes:
    """Fetch an image from a URL."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=400, detail=f"Failed to fetch image from {url}")
            return await response.read()


async def process_image(image_bytes: bytes, background_bytes: bytes) -> bytes:
    """Process the image by removing background and adding it to a new background."""
    async with aiohttp.ClientSession() as session:
        data = {'image': image_bytes}
        async with session.post(OPTIONS[MODE]['url'],
                                data=data,
                                headers=OPTIONS[MODE]['headers']) as response:
            if response.status != 200:
                raise HTTPException(status_code=500, detail="Error processing image")
            resp_json = await response.json()

        img_b64 = resp_json['results'][0]['entities'][0]['image'].encode('utf8')
        processed_img_bytes = base64.decodebytes(img_b64)

    # Open processed image and background image
    processed_img = Image.open(io.BytesIO(processed_img_bytes)).convert("RGBA")
    background_img = Image.open(io.BytesIO(background_bytes)).convert("RGBA")

    # Resize processed image to fit background if necessary
    processed_img = processed_img.resize((background_img.width, background_img.height), Image.LANCZOS)

    # Paste the processed image onto the background image
    background_img.paste(processed_img, (0, 0), processed_img)

    # Save the final image to a byte stream
    output_stream = io.BytesIO()
    background_img.save(output_stream, format="PNG")
    output_stream.seek(0)
    return output_stream.read()


@app.post("/process-image")
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


if __name__ == "__api__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
