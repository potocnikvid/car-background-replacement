from pydantic import BaseModel

class ImageProcessingRequest(BaseModel):
    image_url: str
    background_url: str