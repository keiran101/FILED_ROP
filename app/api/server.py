import asyncio
from time import time

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.api.routes.files import router as files_router
from app.core.config import settings
from app.core import pins
from app.core.logger import logger

_ONE_DAY = 86400


def _do_cleanup() -> None:
    pinned = pins.load()
    now = time()
    for p in list(settings.upload_dir.iterdir()):
        if p.name.startswith('.') or not p.is_file():
            continue
        age = now - p.stat().st_mtime
        if age > _ONE_DAY and p.name not in pinned:
            p.unlink(missing_ok=True)
            pins.remove(p.name)
            logger.info("AUTO-DEL | %s (%.1f h old)", p.name, age / 3600)


async def _cleanup_loop() -> None:
    while True:
        _do_cleanup()
        await asyncio.sleep(3600)


app = FastAPI(title="FileDrop")
app.include_router(files_router)


@app.on_event("startup")
async def startup() -> None:
    asyncio.create_task(_cleanup_loop())


@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    if request.method == "POST" and request.url.path == "/api/upload":
        cl = request.headers.get("content-length")
        if cl and int(cl) > settings.max_file_size_mb * 1024 * 1024:
            pwd = request.headers.get("x-upload-password", "")
            if not (settings.bypass_password and pwd == settings.bypass_password):
                return JSONResponse(
                    status_code=413,
                    content={"detail": f"超过上传限制 {settings.max_file_size_mb}MB"},
                )
    return await call_next(request)

templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "max_mb": settings.max_file_size_mb, "has_bypass": bool(settings.bypass_password)},
    )
