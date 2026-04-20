# to bring os.getenv()
import os

# to bring load_dotenv() function to load environment variables from a .env file
from dotenv import load_dotenv


from fastapi import FastAPI

# main.py is the house for routers from api folder, and schemas from schemas.py, and also the main entry point for the application
from app.api.health import router as health_router
from app.api.sample import router as sample_router

load_dotenv()  # Load environment variables from .env file

app_name = os.getenv("APP_NAME")
# get debug mode from environment variable, default to false if not set and convert to boolean
debug_mode = os.getenv("DEBUG", "false").lower() == "true"


app = FastAPI(title=app_name, debug=debug_mode)


@app.get("/")
def read_root():
    return {
        "message": "Amazn't backend is running",
        "debug": debug_mode,
    }


app.include_router(health_router)
app.include_router(sample_router)
