from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: str = None
    disabled: bool = None

    class Config:
        orm_mode = True