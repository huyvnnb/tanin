import logging
import sys
from enum import Enum

RESET = "\x1b[0m"
GREEN = "\x1b[32m"
BLUE = "\x1b[34m"
YELLOW = "\x1b[33m"
RED = "\x1b[31m"
BOLD = "\x1b[1m"


class Module(Enum):
    APP = "APPLICATION"
    SYS = "SYSTEM"
    CONFIG = "CONFIG"
    SECURITY = "SECURITY"
    DEP = "DEPENDENCY"
    MID = "MIDDLEWARE"

    # DB
    DB = "DATABASE"

    # Base
    BASE_REPO = "BASE REPO"

    # User
    USER_REPO = "USER REPO"
    USER_SERVICE = "USER SERVICE"
    USER_ROUTER = "USER ROUTER"

    # Admin
    ADMIN_SERVICE = "ADMIN SERVICE"
    ADMIN_ROUTER = "ADMIN ROUTER"

    # Role
    ROLE_REPO = "ROLE REPO"
    ROLE_SERVICE = "ROLE SERVICE"
    ROLE_ROUTER = "ROLE ROUTER"

    # Chat
    WEBSOCKET = "WEBSOCKET"

    # Auth
    AUTH_SERVICE = "AUTH SERVICE"
    AUTH_ROUTER = "AUTH ROUTER"
    SESSION_ROUTER = "SESSION ROUTER"


class UvicornLikeFormatter(logging.Formatter):
    LEVEL_COLOR = {
        "INFO": GREEN,
        "DEBUG": BLUE,
        "WARNING": YELLOW,
        "ERROR": RED,
        "CRITICAL": RED,
    }

    def format(self, record):
        original_levelname = record.levelname
        level_color = self.LEVEL_COLOR.get(original_levelname, RESET)

        record.levelname = f"{BOLD}{level_color}{original_levelname + ':':<9}{RESET}"

        formatted_time = self.formatTime(record, self.datefmt)
        record.asctime = f"{BOLD}{GREEN}{formatted_time}{RESET}"

        log_message = super().format(record)
        record.levelname = original_levelname

        return log_message


LOG_FORMAT = "%(levelname)s %(asctime)s - [%(name)s] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str | Enum = "uvicorn", level: int = logging.DEBUG) -> logging.Logger:
    if isinstance(name, Enum):
        name = name.value

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.hasHandlers():
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = UvicornLikeFormatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

    return logger
