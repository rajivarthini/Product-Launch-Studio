from pathlib import Path
from typing import Optional

import cloudinary
import cloudinary.uploader

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class StorageService:
    def __init__(self) -> None:
        self.use_cloudinary = settings.USE_CLOUDINARY
        self.local_upload_dir = Path(settings.LOCAL_UPLOAD_DIR)
        self.local_upload_dir.mkdir(parents=True, exist_ok=True)

        if self.use_cloudinary:
            # TODO: Only configure when credentials are provided.
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET,
                secure=True,
            )

    async def save_image(
        self, content: bytes, filename: str, folder: str = "product-launch-studio"
    ) -> str:
        # Always save locally first (do not overwrite existing files)
        path = self.local_upload_dir / filename

        if path.exists():
            i = 1
            stem = path.stem
            suffix = path.suffix
            while True:
                candidate = self.local_upload_dir / f"{stem}_{i}{suffix}"
                if not candidate.exists():
                    path = candidate
                    break
                i += 1

        try:
            path.write_bytes(content)
        except Exception as exc:
            logger.exception("Failed writing local image %s: %s", path, exc)

        # Attempt Cloudinary upload after local save (do not change return value)
        if self.use_cloudinary and settings.CLOUDINARY_CLOUD_NAME:
            try:
                cloudinary.uploader.upload(
                    content,
                    folder=folder,
                    public_id=Path(path).stem,
                    overwrite=True,
                    resource_type="image",
                )
            except Exception as exc:  # noqa: BLE001
                logger.exception("Cloudinary upload failed (local copy kept): %s", exc)

        return str(path)