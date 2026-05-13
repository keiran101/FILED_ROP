import re
from pathlib import Path
from typing import List

import aiofiles
from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.logger import log_upload, log_download, log_delete
from app.core import rate_limiter, pins

router = APIRouter(prefix="/api")


def _safe_name(name: str) -> str:
    name = Path(name).name
    name = re.sub(r'[^\w\-_\. ]', '_', name)
    name = name.strip('. ')
    return name or 'file'


def _check_path(path: Path) -> Path:
    resolved = path.resolve()
    upload = settings.upload_dir.resolve()
    try:
        resolved.relative_to(upload)
    except ValueError:
        raise HTTPException(403, "Access denied")
    return resolved


@router.post("/check-password")
async def check_password(request: Request):
    pwd = request.headers.get("x-upload-password", "")
    if not settings.bypass_password or pwd != settings.bypass_password:
        raise HTTPException(401, "密码错误")
    return {"ok": True}


@router.post("/upload")
async def upload_files(request: Request, files: List[UploadFile] = File(...)):
    ip = request.client.host
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    pwd = request.headers.get("x-upload-password", "")
    has_bypass = bool(settings.bypass_password and pwd == settings.bypass_password)
    uploaded = []
    for file in files:
        if not rate_limiter.check(ip, settings.rate_limit):
            raise HTTPException(429, f"上传过于频繁，每分钟最多 {settings.rate_limit} 个文件")
        name = _safe_name(file.filename or 'file')
        dest = settings.upload_dir / name
        if dest.exists():
            stem, suffix = Path(name).stem, Path(name).suffix
            i = 1
            while dest.exists():
                dest = settings.upload_dir / f"{stem}_{i}{suffix}"
                i += 1
        received = 0
        try:
            async with aiofiles.open(dest, "wb") as f:
                while True:
                    chunk = await file.read(1024 * 1024)
                    if not chunk:
                        break
                    received += len(chunk)
                    if not has_bypass and received > max_bytes:
                        dest.unlink(missing_ok=True)
                        raise HTTPException(413, f"文件超过 {settings.max_file_size_mb}MB 限制")
                    await f.write(chunk)
        except HTTPException:
            raise
        except Exception:
            dest.unlink(missing_ok=True)
            raise
        log_upload(ip, dest.name, dest.stat().st_size)
        uploaded.append(dest.name)
    return {"uploaded": uploaded}


@router.get("/files")
async def list_files():
    pinned_set = pins.load()
    files = []
    for p in sorted(settings.upload_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if p.is_file() and not p.name.startswith('.'):
            stat = p.stat()
            files.append({
                "name": p.name,
                "size": stat.st_size,
                "mtime": stat.st_mtime,
                "pinned": p.name in pinned_set,
            })
    return files


@router.post("/files/{filename}/pin")
async def pin_file(filename: str):
    path = _check_path(settings.upload_dir / filename)
    if not path.exists() or not path.is_file():
        raise HTTPException(404, "File not found")
    pinned = pins.toggle(filename)
    return {"pinned": pinned}


@router.get("/files/{filename}")
async def download_file(request: Request, filename: str):
    path = _check_path(settings.upload_dir / filename)
    if not path.exists() or not path.is_file():
        raise HTTPException(404, "File not found")
    log_download(request.client.host, path.name, path.stat().st_size)
    return FileResponse(path, filename=path.name, media_type="application/octet-stream")


@router.delete("/files/{filename}")
async def delete_file(request: Request, filename: str):
    path = _check_path(settings.upload_dir / filename)
    if not path.exists() or not path.is_file():
        raise HTTPException(404, "File not found")
    log_delete(request.client.host, path.name)
    path.unlink()
    pins.remove(filename)
    return {"deleted": filename}
