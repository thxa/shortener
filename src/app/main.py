from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from .database import create_db_pool, close_db_pool
from .dependencies import init_limiter, close_limiter
from .routers import shortener, redirect, index
# from fastapi.staticfiles import StaticFiles

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize services
    await init_limiter()
    db_pool = await create_db_pool()
    yield {"db_pool": db_pool}
    # Cleanup services
    await close_limiter()
    await close_db_pool(db_pool)

app = FastAPI(lifespan=lifespan)

# app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(index.router)
app.include_router(shortener.router)
app.include_router(redirect.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
