from fastapi import FastAPI
from app.api import endpoints

app = FastAPI()

# Include routers or individual endpoints
app.include_router(endpoints.router)

@app.get("/")
async def root():
    return {"message": "Server is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
