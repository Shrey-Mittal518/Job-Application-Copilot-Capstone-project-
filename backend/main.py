from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import engine
from models import Base
from routes.auth import router as auth_router
from routes.applications import router as app_router
from routes.drafts import router as drafts_router
from routes.scraper import router as scraper_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Job Application Co-Pilot API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(app_router)
app.include_router(drafts_router)
app.include_router(scraper_router)


@app.get("/health")
def health():
    return {"status": "ok"}