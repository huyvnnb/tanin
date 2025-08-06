import asyncio
import sys

from tanin.websocket import endpoints

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import time

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from tanin.api.endpoints import session_router
from tanin.core.exceptions import APIException
from fastapi import Request
from tanin.core.handlers import api_exception_handler, validation_exception_handler, general_exception_handler
from tanin.utils import logger
from tanin.utils.logger import Module

app = FastAPI()
logger = logger.get_logger(Module.SYS)

app.include_router(session_router.router)
app.include_router(endpoints.router)

app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


@app.middleware("http")
async def log_process_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    log_message = f"{request.method} {request.url.path} took {round(duration * 1000, 2)}ms"
    print(log_message)
    logger.info(log_message)

    return response


@app.get("/")
def hello():
    return {"message": "Welcome to Tanin API"}
