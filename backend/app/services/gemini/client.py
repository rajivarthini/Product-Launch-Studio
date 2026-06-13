import json
import re
import asyncio
import base64
from typing import Any, Dict, Optional

import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class GeminiClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.base_url = base_url or settings.GEMINI_API_BASE_URL
        self.model_name = model_name or settings.GEMINI_MODEL_NAME or "models/gemini-1.5-flash"

    @staticmethod
    def _extract_json_from_text(text: str) -> str:
        """Strip markdown fences and extract the outermost JSON object."""
        # Try to strip ```json ... ``` fences first
        match = re.search(r"```(?:json)?\s*(\{.*\}|\[.*\])\s*```", text, re.DOTALL)
        if match:
            return match.group(1)
        # Otherwise, find first { ... last }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return text[start : end + 1]
        return text

    async def _generate_via_langchain(
        self, prompt: str, image_paths: Optional[list] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Try LangChain path. Returns None if langchain is not installed (skip to REST).
        Raises ValueError on any other failure.
        """
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.messages import HumanMessage
        except ImportError:
            logger.warning("langchain-google-genai not installed; skipping LangChain path.")
            return None  # Signal to fall through to REST API

        model_name = (self.model_name or "").split("/")[-1]
        if not model_name:
            raise ValueError("No Gemini model name configured")

        logger.debug("=== GEMINI LANGCHAIN CALL ===")
        logger.debug("Model: %s", model_name)
        logger.debug("Prompt (first 500 chars): %s", prompt[:500])
        logger.debug("Image paths: %s", image_paths)

        llm = ChatGoogleGenerativeAI(
            model=model_name,
            api_key=self.api_key,
            temperature=0,
        )

        content: Any
        if image_paths:
            content = [{"type": "text", "text": prompt}]
            for img_path in image_paths:
                try:
                    with open(img_path, "rb") as f:
                        image_data = base64.b64encode(f.read()).decode("utf-8")
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                    })
                    logger.debug("Added image to LangChain payload: %s", img_path)
                except Exception as e:
                    logger.error("Failed to load image %s for LangChain: %s", img_path, e)
                    raise ValueError(f"Cannot read image file {img_path}: {e}") from e
        else:
            content = prompt
            logger.debug("No images included in LangChain call.")

        resp = await llm.ainvoke([HumanMessage(content=content)])
        text = getattr(resp, "content", "") or ""
        if isinstance(text, list):
            text = "".join(
                str(part.get("text", part)) if isinstance(part, dict) else str(part)
                for part in text
            )

        logger.info("=== GEMINI LANGCHAIN RAW RESPONSE ===\n%s", text)

        if not text.strip():
            raise ValueError("LangChain returned empty text response from Gemini")

        json_text = self._extract_json_from_text(text)
        logger.debug("Extracted JSON text (LangChain): %s", json_text)

        try:
            parsed = json.loads(json_text)
        except json.JSONDecodeError as jde:
            logger.error(
                "JSON parse failed (LangChain). Raw text:\n%s\nError: %s", text, jde
            )
            raise ValueError(f"LangChain JSON parse error: {jde}. Raw text: {text[:300]}") from jde

        logger.info("=== GEMINI LANGCHAIN PARSED JSON ===\n%s", json.dumps(parsed, indent=2)[:500])
        return parsed

    async def generate_json(
        self,
        prompt: str,
        image_paths: Optional[list] = None,
        image_path: Optional[str] = None,
        extra_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Call Gemini to generate a JSON response.

        Tries LangChain first, then falls back to direct REST API.
        NEVER returns an empty dict silently. Raises ValueError on any failure.
        """
        # Normalise: legacy callers may use singular image_path
        if image_path and not image_paths:
            image_paths = [image_path]

        logger.info("=== generate_json called ===")
        logger.info("API key configured: %s", bool(self.api_key))
        logger.info("Model: %s", self.model_name)
        logger.info("Image paths: %s", image_paths)
        logger.info("Prompt (first 300 chars): %s", prompt[:300])

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured. Set it in your .env file."
            )

        # --- 1) Try LangChain ---
        try:
            lc_result = await self._generate_via_langchain(prompt, image_paths)
            if lc_result is not None:  # None means langchain not installed; fall through
                return lc_result
        except Exception as lc_exc:
            logger.error("LangChain path failed: %s", lc_exc)
            logger.info("Falling through to direct REST API call.")

        # --- 2) Direct REST API ---
        url = f"{self.base_url}/{self.model_name}:generateContent"
        logger.debug("REST URL: %s", url)

        payload: Dict[str, Any] = {
            "contents": [
                {
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
            },
        }

        if image_paths:
            for img_path in image_paths:
                try:
                    with open(img_path, "rb") as f:
                        img_data = base64.b64encode(f.read()).decode("utf-8")
                    payload["contents"][0]["parts"].append({
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": img_data,
                        }
                    })
                    logger.debug("Added image to REST payload: %s", img_path)
                except Exception as e:
                    logger.error("Failed to read image %s: %s", img_path, e)
                    raise ValueError(f"Cannot read image file {img_path}: {e}") from e
        else:
            logger.debug("No images sent to REST API.")

        if extra_payload:
            payload.update(extra_payload)

        max_retries = 3
        data: Dict[str, Any] = {}

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=60) as http_client:
                    resp = await http_client.post(
                        url,
                        headers={"Content-Type": "application/json"},
                        params={"key": self.api_key},
                        json=payload,
                    )
                    logger.info(
                        "REST API response status: %s (attempt %d/%d)",
                        resp.status_code,
                        attempt + 1,
                        max_retries,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    break  # success

            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                body = ""
                try:
                    body = exc.response.text
                except Exception:
                    pass
                logger.error(
                    "Gemini REST API HTTP %s error (attempt %d/%d): %s\nResponse body: %s",
                    status_code,
                    attempt + 1,
                    max_retries,
                    exc,
                    body,
                )
                if status_code == 429 and attempt < max_retries - 1:
                    delays = [2, 5, 10]
                    wait_time = delays[attempt]
                    logger.warning("Rate limited (429). Retrying in %s seconds...", wait_time)
                    await asyncio.sleep(wait_time)
                    continue
                raise ValueError(
                    f"Gemini API returned HTTP {status_code}. Body: {body[:500]}"
                ) from exc

            except Exception as exc:
                logger.exception("Unexpected error calling Gemini REST API: %s", exc)
                raise ValueError(f"Unexpected Gemini REST API error: {exc}") from exc

        # --- Parse the REST response ---
        full_response_text = json.dumps(data)
        logger.debug("Full Gemini REST response: %s", full_response_text[:2000])

        candidates = data.get("candidates", [])
        if not candidates:
            logger.error(
                "Gemini returned no candidates. Full response:\n%s", full_response_text
            )
            raise ValueError(
                f"Gemini returned no candidates. Full response: {full_response_text[:500]}"
            )

        finish_reason = candidates[0].get("finishReason", "")
        if finish_reason not in ("STOP", ""):
            logger.error(
                "Gemini finishReason is '%s' (not STOP). Full response:\n%s",
                finish_reason,
                full_response_text,
            )
            raise ValueError(
                f"Gemini did not finish cleanly. finishReason='{finish_reason}'. Full response: {full_response_text[:500]}"
            )

        text = (
            candidates[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )

        logger.info("=== GEMINI REST RAW TEXT RESPONSE ===\n%s", text)

        if not text.strip():
            raise ValueError(
                f"Gemini returned empty text in candidates[0]. Full response: {full_response_text[:500]}"
            )

        json_text = self._extract_json_from_text(text)
        logger.debug("Extracted JSON text (REST): %s", json_text[:500])

        try:
            parsed = json.loads(json_text)
        except json.JSONDecodeError as jde:
            logger.error(
                "JSON parse failed (REST API). Raw Gemini text:\n%s\nError: %s",
                text,
                jde,
            )
            raise ValueError(
                f"Gemini response is not valid JSON. Parse error: {jde}. Raw text: {text[:500]}"
            ) from jde

        logger.info("=== GEMINI REST PARSED JSON ===\n%s", json.dumps(parsed, indent=2)[:1000])
        return parsed
