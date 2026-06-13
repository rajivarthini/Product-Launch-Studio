from fastapi import UploadFile, HTTPException, status

ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


class ImageValidationService:
    @staticmethod
    def validate_upload(file: UploadFile, field_name: str) -> None:
        if file.content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid content type for {field_name}. "
                f"Expected one of {sorted(ALLOWED_IMAGE_CONTENT_TYPES)}.",
            )

