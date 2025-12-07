from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routes import setup_routes

app = FastAPI(title="Hopper API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://hopper-app-gamma.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configura as rotas
setup_routes(app)


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)

