import asyncio
import sys
import uvicorn

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


if __name__ == '__main__':
    uvicorn.run("src.tanin.main:app", host="0.0.0.0", port=8000, reload=True, )
