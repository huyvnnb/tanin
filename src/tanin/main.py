import asyncio
from contextlib import asynccontextmanager

from tanin.core.config import settings
from tanin.core.dependencies import get_connection_manager
from tanin.websocket import endpoints

import time

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from tanin.api.endpoints import session_router, webrtc_router, auth_router
from tanin.core.exceptions import APIException
from fastapi import Request
from tanin.core.handlers import api_exception_handler, validation_exception_handler, general_exception_handler
from tanin.utils import logger
from tanin.utils.logger import Module
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

logger = logger.get_logger(Module.SYS)
logger.info(f"[{__name__}] Current event loop policy: {type(asyncio.get_event_loop_policy()).__name__}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Docs: http://localhost:8000/docs")

    manager = get_connection_manager()

    logger.info("Server is starting up, initializing Pub/Sub listener...")
    pubsub_listener_task = asyncio.create_task(manager.pubsub_listener())

    async_engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=True)
    session_factory = async_sessionmaker(
        async_engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
        class_=AsyncSession
    )

    app.state.async_engine = async_engine  # type: ignore[attr-defined]
    app.state.session_factory = session_factory  # type: ignore[attr-defined]

    yield

    logger.info("Server is shutting down, cleaning up background tasks...")

    pubsub_listener_task.cancel()
    try:
        await pubsub_listener_task
    except asyncio.CancelledError:
        logger.info("Pub/Sub listener task was cancelled successfully.")


app = FastAPI(
    title="Tanin",
    lifespan=lifespan
)


app.include_router(session_router.router)
app.include_router(endpoints.router)
app.include_router(webrtc_router.router)
app.include_router(auth_router.router)

app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.middleware("http")
async def log_process_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    log_message = f"{request.method} {request.url.path} took {round(duration * 1000, 2)}ms"
    logger.info(log_message)

    return response


@app.get("/")
def hello():
    return {"message": "Welcome to Tanin API"}
