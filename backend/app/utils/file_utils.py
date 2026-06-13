from pathlib import Path
from typing import Tuple

from fastapi import UploadFile

from app.core.logging import get_logger

logger = get_logger(__name__)


def get_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


async def read_upload_bytes(upload: UploadFile) -> Tuple[bytes, str]:
    data = await upload.read()
    ext = get_extension(upload.filename or "")
    return data, ext

