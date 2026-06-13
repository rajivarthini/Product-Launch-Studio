## Product Launch Studio - Backend

FastAPI backend providing a single `POST /api/full-workflow` endpoint that runs the complete AI-assisted product launch workflow.

### Features

- Single multipart `POST /api/full-workflow` endpoint.
- Product and license image uploads, validation, and storage (Cloudinary or local).
- Product image enhancement via Pillow (no new views, no hallucination).
- Platform rules service for Amazon, Flipkart, and Meesho.
- Gemini integration wrappers with prompt templates and strict JSON validation via Pydantic.
- Packaging recommendation and intermediate dieline payload.
- Strongly-typed response matching the specified JSON shape.

### Running locally

```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate  # Windows
pip install -r requirements.txt

cp .env.example .env  # edit if needed

uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. The main public endpoint is `POST /api/full-workflow`.

### Notes

- If `GEMINI_API_KEY` is not configured, the Gemini client will return deterministic mock responses for development.
- If Cloudinary credentials are missing or upload fails, images are saved under `backend/uploads` and local paths are returned.
- OCR for license images is currently a placeholder; integrate a real OCR provider as needed and remove the stub.
- True dieline/export is not implemented; `dieline_template_status` clearly indicates the need for an external renderer.

