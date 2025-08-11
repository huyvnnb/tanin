import asyncio
import sys
from contextlib import asynccontextmanager

from tanin.core.config import settings
from tanin.core.dependencies import get_connection_manager
from tanin.websocket import endpoints

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import time

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from tanin.api.endpoints import session_router, webrtc_router
from tanin.core.exceptions import APIException
from fastapi import Request
from tanin.core.handlers import api_exception_handler, validation_exception_handler, general_exception_handler
from tanin.utils import logger
from tanin.utils.logger import Module
from starlette.middleware.cors import CORSMiddleware

logger = logger.get_logger(Module.SYS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    manager = get_connection_manager()

    logger.info("Server is starting up, initializing Pub/Sub listener...")
    pubsub_listener_task = asyncio.create_task(manager.pubsub_listener())

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
