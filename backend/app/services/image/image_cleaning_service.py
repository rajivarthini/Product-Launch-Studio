from io import BytesIO
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageEnhance

try:
    from rembg import remove as rembg_remove
except Exception:
    rembg_remove = None

# Gemini
try:
    from google import genai
    from google.genai import types
except Exception:
    genai = None

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ImageCleaningService:

    def __init__(self, upload_dir: str) -> None:
        self.base_dir = Path(upload_dir)

        self.original_dir = self.base_dir / "original"
        self.cleaned_dir = self.base_dir / "cleaned"

        self.original_dir.mkdir(parents=True, exist_ok=True)
        self.cleaned_dir.mkdir(parents=True, exist_ok=True)

        # Gemini client
        self.client = None
        if genai and settings.GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            except Exception:
                logger.warning("Gemini client initialization failed.")

    def clean_image(self, image_bytes: bytes, filename: str, description: str = ""):

        logger.info(f"Processing '{filename}' for product: '{description}'")

        # ---------------------------------------------------
        # Generate Unique Filename
        # ---------------------------------------------------

        unique_id = uuid4().hex
        safe_filename = f"{unique_id}_{filename}"

        original_path = self.original_dir / safe_filename
        cleaned_path = self.cleaned_dir / safe_filename

        # ---------------------------------------------------
        # Save Original Image
        # ---------------------------------------------------

        with open(original_path, "wb") as f:
            f.write(image_bytes)

        prompt = """
Edit the uploaded product photo for professional e-commerce use.

Instructions:
• Detect the primary product in the image.
• Remove the entire background completely.
• Remove all extra objects, scenery, floor, reflections, shadows, props, and clutter.
• Keep ONLY the actual product visible.
• Preserve the product’s real shape, color, texture, branding, and proportions.
• Do NOT redesign or hallucinate new product parts.
• Place the product centered on a pure white background (#FFFFFF).
• Produce a clean marketplace-ready product image suitable for Amazon, Flipkart, and Meesho.
• Return only the edited image.
"""

        logger.info("Prompt sent to Gemini.")

        # ---------------------------------------------------
        # ---------------------------------------------------
        # 1️⃣ PRIMARY → REMBG BACKGROUND REMOVAL
        # ---------------------------------------------------

        try:
            if rembg_remove is None:
                raise ImportError("rembg not available")

            cleaned_bytes = rembg_remove(image_bytes)

            with Image.open(BytesIO(cleaned_bytes)) as rembg_img:

                rembg_img = rembg_img.convert("RGBA")

                white_bg = Image.new("RGBA", rembg_img.size, (255, 255, 255, 255))
                composed = Image.alpha_composite(white_bg, rembg_img)

                product = composed.convert("RGB")

                enhancer = ImageEnhance.Sharpness(product)
                product = enhancer.enhance(1.1)

                contrast = ImageEnhance.Contrast(product)
                product = contrast.enhance(1.05)

                buf = BytesIO()
                product.save(buf, format="JPEG", quality=95)

                with open(cleaned_path, "wb") as f:
                    f.write(buf.getvalue())

                logger.info("rembg background removal successful.")

                return {
                    "original_image": f"/uploads/original/{safe_filename}",
                    "cleaned_image": f"/uploads/cleaned/{safe_filename}",
                }

        except Exception as e:
            logger.warning("rembg cleaning failed: %s", e)

        # ---------------------------------------------------
        # 2️⃣ FALLBACK → GEMINI IMAGE CLEANING
        # ---------------------------------------------------

        try:
            if self.client:

                response = self.client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=[
                        prompt,
                        types.Part.from_bytes(
                            data=image_bytes,
                            mime_type="image/jpeg",
                        ),
                    ],
                )

                for part in response.candidates[0].content.parts:
                    if hasattr(part, "inline_data") and part.inline_data:

                        cleaned_bytes = part.inline_data.data

                        with open(cleaned_path, "wb") as f:
                            f.write(cleaned_bytes)

                        logger.info("Gemini cleaning successful.")

                        return {
                            "original_image": f"/uploads/original/{safe_filename}",
                            "cleaned_image": f"/uploads/cleaned/{safe_filename}",
                        }

        except Exception as e:
            logger.warning("Gemini cleaning fallback failed: %s", e)

        # ---------------------------------------------------
        # 3️⃣ LAST FALLBACK → RETURN ORIGINAL
        # ---------------------------------------------------

        try:
            with Image.open(BytesIO(image_bytes)) as img:

                img = img.convert("RGB")

                buf = BytesIO()
                img.save(buf, format="JPEG", quality=95)

                with open(cleaned_path, "wb") as f:
                    f.write(buf.getvalue())

                logger.info("Returned original image as fallback.")

                return {
                    "original_image": f"/uploads/original/{safe_filename}",
                    "cleaned_image": f"/uploads/cleaned/{safe_filename}",
                }

        except Exception:
            return None