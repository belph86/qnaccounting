from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.app.core.database import init_db
from src.app.api.routes.auth import router as auth_router
from src.app.api.routes.accounts import router as accounts_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="CS Banking Agent",
    description="API server for AI agent that automatically matches bank transactions with invoices via Česká spořitelna API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(accounts_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
