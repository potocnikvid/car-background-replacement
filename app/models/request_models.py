from pydantic import BaseModel
from app.models.enums import CarPosition

class ImageProcessingRequest(BaseModel):
    image_url: str
    background_url: str
    position: CarPosition