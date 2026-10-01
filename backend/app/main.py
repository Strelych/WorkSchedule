from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.routers.bot_api import router as bot_router
from app.routers.website_api import router as website_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Valet Scheduler API", version="0.1.0", lifespan=lifespan)

app.include_router(bot_router)
app.include_router(website_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
