from fastapi import HTTPException, status


def validate_positive_float(value: float, field_name: str) -> None:
    if value <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} must be greater than zero.",
        )

