from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends

from app.schemas.workflow import WorkflowResponse
from app.schemas.platform_rules import PlatformEnum
from app.services.workflow.orchestrator import WorkflowOrchestrator
from app.core.logging import get_logger

from typing import Optional

router = APIRouter()
logger = get_logger(__name__)


def get_orchestrator() -> WorkflowOrchestrator:
    return WorkflowOrchestrator()


@router.post(
    "/full-workflow",
    response_model=WorkflowResponse,
    status_code=status.HTTP_200_OK,
)
async def full_workflow(
    product_image: UploadFile | str | None = File(None),
    license_image: UploadFile | str | None = File(None),
    product_image_2: UploadFile | str | None = File(None),
    product_image_3: UploadFile | str | None = File(None),
    product_image_4: UploadFile | str | None = File(None),
    height: str = Form(...),
    width: str = Form(...),
    weight: str = Form(...),
    description: str = Form(...),
    platform: str = Form(...),
    product_name_hint: str | None = Form(None),
    product_material_hint: str | None = Form(None),
    dimension_unit: str = Form("cm"),
    weight_unit: str = Form("g"),
    orchestrator: WorkflowOrchestrator = Depends(get_orchestrator),
) -> WorkflowResponse:
    try:
        logger.debug("--- [DEBUG] Full Workflow Inputs ---")
        logger.debug("platform: %s (%s)", platform, type(platform))
        logger.debug("height: %s (%s)", height, type(height))
        logger.debug("width: %s (%s)", width, type(width))
        logger.debug("weight: %s (%s)", weight, type(weight))
        logger.debug("description: %s", description)

        platform_lower = platform.lower().strip()
        try:
            platform_enum = PlatformEnum(platform_lower)
        except ValueError:
            valid_platforms = [p.value for p in PlatformEnum]
            logger.error("Invalid platform selected: %s. Valid options: %s", platform, valid_platforms)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid platform '{platform}'. Supported: {valid_platforms}"
            )

        try:
            f_height = float(height)
            f_width = float(width)
            f_weight = float(weight)
        except ValueError as e:
            logger.error("Numeric conversion failed: %s", e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Numeric field validation failed: {e}"
            )

        # 2. Collect and filter product images
        raw_images = [product_image, product_image_2, product_image_3, product_image_4]
        product_images = []
        for idx, img in enumerate(raw_images):
            if img is not None and hasattr(img, "filename") and img.filename:
                logger.info("Received product_image_%d: %s", idx + 1, img.filename)
                product_images.append(img)
            else:
                logger.info(
                    "product_image_%d skipped: value=%s type=%s",
                    idx + 1,
                    img,
                    type(img),
                )

        logger.info("Total valid product images received: %d", len(product_images))

        if not product_images:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one product image is required.",
            )

        # 3. Handle license image
        valid_license = None
        if license_image is not None and hasattr(license_image, "filename") and license_image.filename:
            logger.info("Received license_image: %s", license_image.filename)
            valid_license = license_image
        else:
            logger.info(
                "license_image skipped: value=%s type=%s",
                license_image,
                type(license_image),
            )

        result = await orchestrator.run_full_workflow(
            product_images=product_images,
            license_image=valid_license,
            height=f_height,
            width=f_width,
            weight=f_weight,
            description=description,
            platform=platform_enum,
            product_name_hint=product_name_hint,
            product_material_hint=product_material_hint,
            dimension_unit=dimension_unit,
            weight_unit=weight_unit,
        )
        return result
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected error in /full-workflow: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"[DEBUG] Workflow failed: {type(exc).__name__}: {exc}",
        ) from exc