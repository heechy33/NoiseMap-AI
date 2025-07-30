from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router as noise_router
from dotenv import load_dotenv


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(noise_router) 
