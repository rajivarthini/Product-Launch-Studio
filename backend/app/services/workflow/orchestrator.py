import os
import uuid
from typing import Any, Dict

from fastapi import UploadFile

from app.core.constants import (
    IMAGE_ENHANCEMENT_DISCLAIMER,
    LICENSE_ANALYSIS_DISCLAIMER,
    PACKAGING_DESIGN_DISCLAIMER,
    PLATFORM_DISCLAIMER,
)
from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.platform_rules import PlatformEnum, PlatformInfo
from app.schemas.workflow import WorkflowResponse, WorkflowInputs, ImagesResponse
from app.schemas.product import ProductAnalysis
from app.schemas.license import LicenseAnalysis
from app.schemas.listing import Listing
from app.schemas.packaging import PackagingInfo
from app.schemas.pricing import PricingInfo
from app.services.image.image_validation_service import ImageValidationService
from app.services.image.image_cleaning_service import ImageCleaningService
from app.services.storage.cloudinary_service import StorageService
from app.services.platform.platform_rules_service import PlatformRulesService
from app.services.gemini.product_analysis_service import ProductAnalysisService
from app.services.gemini.license_analysis_service import LicenseAnalysisService
from app.services.gemini.listing_service import ListingService
from app.services.gemini.combined_analysis_service import CombinedAnalysisService
from app.services.packaging.packaging_recommendation_service import (
    PackagingRecommendationService,
)
from app.services.packaging.dieline_service import DielineService
from app.services.pricing.pricing_service import PricingService

logger = get_logger(__name__)


class WorkflowOrchestrator:
    def __init__(self) -> None:
        self.image_validator = ImageValidationService()
        self.image_cleaner = ImageCleaningService(settings.LOCAL_UPLOAD_DIR)
        self.storage = StorageService()
        self.platform_rules_service = PlatformRulesService()
        self.product_analysis_service = ProductAnalysisService()
        self.license_analysis_service = LicenseAnalysisService()
        self.listing_service = ListingService()
        self.combined_analysis_service = CombinedAnalysisService()
        self.packaging_recommendation_service = PackagingRecommendationService()
        self.dieline_service = DielineService()
        self.pricing_service = PricingService()

    async def run_full_workflow(
        self,
        product_images: list[UploadFile] | None = None,
        product_image: UploadFile | None = None,
        license_image: UploadFile | None = None,
        height: float = 0,
        width: float = 0,
        weight: float = 0,
        description: str = "",
        platform: PlatformEnum = None,
        product_name_hint: str | None = None,
        product_material_hint: str | None = None,
        dimension_unit: str = "cm",
        weight_unit: str = "g",
    ) -> WorkflowResponse:

        # Normalize inputs so both 'product_image' and 'product_images' work
        if product_images is None:
            product_images = []

        if product_image is not None:
            product_images.append(product_image)

        # 3️⃣ Use configured uploads directory
        UPLOAD_DIR = settings.LOCAL_UPLOAD_DIR

        logger.info("CRITICAL: Absolute Storage Directory -> %s", UPLOAD_DIR)
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Inject the correct absolute path into the cleaner
        self.image_cleaner.upload_dir = UPLOAD_DIR

        # Ensure StorageService writes to the same uploads folder
        try:
            from pathlib import Path

            self.storage.local_upload_dir = Path(UPLOAD_DIR)
            self.storage.local_upload_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            logger.exception("Failed to set storage local_upload_dir to %s", UPLOAD_DIR)

        has_product_images = len(product_images) > 0
        logger.info("run_full_workflow started with %d product images", len(product_images))

        if not has_product_images:
            logger.warning("No product images provided.")
        else:
            for idx, img in enumerate(product_images):
                logger.debug("Received product_image[%d]: filename=%s", idx, img.filename)

        # 1️⃣ Validate images
        if has_product_images:
            for idx, img in enumerate(product_images):
                self.image_validator.validate_upload(img, f"product_image_{idx+1}")

        has_license = isinstance(license_image, UploadFile) and license_image.filename

        if has_license:
            logger.info("License image provided: %s", license_image.filename)
            self.image_validator.validate_upload(license_image, "license_image")
        else:
            logger.info("No license image provided (optional step skipped)")

        # 2️⃣ Read image bytes
        product_bytes_list = []

        if has_product_images:
            for img in product_images:
                product_bytes_list.append(await img.read())

        license_bytes = b""

        if has_license:
            license_bytes = await license_image.read()

        saved_original_paths = []
        saved_cleaned_paths = []
        saved_original_paths_abs = []

        if has_product_images:
            for idx, p_bytes in enumerate(product_bytes_list):
                img = product_images[idx]
                byte_len = len(p_bytes)

                logger.info("Processing image[%d]: %s (%d bytes)", idx, img.filename, byte_len)

                if byte_len == 0:
                    logger.warning("image[%d] has 0 bytes. Skipping save.", idx)
                    continue

                try:
                    file_ext = "jpg"

                    if img.filename and "." in img.filename:
                        file_ext = img.filename.split(".")[-1]

                    # Save original via StorageService
                    original_filename = f"original_{uuid.uuid4()}.{file_ext}"

                    saved_original_local = await self.storage.save_image(
                        p_bytes, original_filename
                    )

                    saved_original_paths.append(saved_original_local)
                    saved_original_paths_abs.append(os.path.abspath(saved_original_local))

                    logger.info(f"Saved original image: {saved_original_local}")

                    # Clean image
                    cleaned_result = self.image_cleaner.clean_image(
                        p_bytes,
                        original_filename,
                        description=description,
                    )

                    if isinstance(cleaned_result, dict) and "cleaned_image" in cleaned_result:
                        saved_cleaned_local = cleaned_result["cleaned_image"]
                        saved_cleaned_paths.append(saved_cleaned_local)
                        logger.info(f"Saved cleaned image: {saved_cleaned_local}")
                    else:
                        logger.warning("Cleaned image generation failed or returned unexpected format")

                except Exception as e:
                    logger.error(f"Image processing failed for {img.filename}: {e}")

        # Save license image
        license_url = None
        license_url_abs = None

        if has_license:
            try:
                file_ext = "jpg"

                if license_image.filename and "." in license_image.filename:
                    file_ext = license_image.filename.split(".")[-1]

                license_filename = f"license_{uuid.uuid4()}.{file_ext}"

                license_saved = await self.storage.save_image(
                    license_bytes, license_filename
                )

                license_url = license_saved
                license_url_abs = os.path.abspath(license_saved)

                logger.info(f"Saved license image: {license_saved}")

            except Exception as e:
                logger.error(f"License image save failed: {e}")

        # 4️⃣ Load platform rules
        platform_rules = self.platform_rules_service.get_rules(platform)

        platform_info = PlatformInfo(
            selected=platform,
            rules_summary=platform_rules,
        )

        # 5️⃣ Run AI analysis
        product_analysis, license_analysis, listing = await self.combined_analysis_service.analyze(
            description=description,
            platform=platform,
            height=height,
            width=width,
            weight=weight,
            dimension_unit=dimension_unit,
            weight_unit=weight_unit,
            product_name_hint=product_name_hint,
            product_material_hint=product_material_hint,
            product_image_paths=saved_original_paths_abs,
            license_image_path=license_url_abs,
        )

        # 6️⃣ Packaging recommendation
        packaging_info: PackagingInfo = self.packaging_recommendation_service.recommend(
            height=height,
            width=width,
            weight=weight,
            dimension_unit=dimension_unit,
            weight_unit=weight_unit,
            product_analysis=product_analysis,
        )

        # 7️⃣ Dieline generation
        dieline_payload = await self.dieline_service.generate_dieline_payload(packaging_info)

        packaging_info.dieline_payload = dieline_payload

        packaging_info.dieline_download_url = (
            dieline_payload.get("download_url")
            if isinstance(dieline_payload, dict)
            else None
        )

        # 8️⃣ Pricing estimation
        pricing_info: PricingInfo = self.pricing_service.estimate(
            product_analysis=product_analysis,
            description=description,
            platform=platform,
        )

        # 9️⃣ Assemble response
        inputs = WorkflowInputs(
            height=height,
            width=width,
            weight=weight,
            dimension_unit=dimension_unit,
            weight_unit=weight_unit,
            description=description,
        )

        images_block = ImagesResponse(
            original_images=saved_original_paths,
            cleaned_images=saved_cleaned_paths,
        )

        disclaimers = [
            IMAGE_ENHANCEMENT_DISCLAIMER,
            LICENSE_ANALYSIS_DISCLAIMER,
            PLATFORM_DISCLAIMER,
            PACKAGING_DESIGN_DISCLAIMER,
        ]

        return WorkflowResponse(
            success=True,
            platform=platform_info,
            inputs=inputs,
            product_analysis=product_analysis,
            license_analysis=license_analysis,
            listing=listing,
            images=images_block,
            packaging=packaging_info,
            pricing=pricing_info,
            disclaimers=disclaimers,
        )