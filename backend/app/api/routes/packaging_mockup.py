from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
import httpx

router = APIRouter(tags=["packaging-mockup"])

TEMPLATE_IMAGE_MAP = {
    "giftbox": "giftbox.png",
    "matchbox": "matchbox.png",
    "mailer": "mailer.png",
    "pillowpack": "pillowpack.png",
    "boxwithlid": "boxlid.png",
}


@router.get("/api/packaging/mockup/{template_name}")
async def get_packaging_mockup(template_name: str):
    filename = TEMPLATE_IMAGE_MAP.get(template_name.lower())
    print("template_name =", template_name)
    print("mapped filename =", filename)

    if not filename:
        raise HTTPException(status_code=404, detail="Unknown packaging template")

    remote_url = f"https://www.templatemaker.nl/assets/images/{filename}"
    print("remote_url =", remote_url)

    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            resp = await client.get(remote_url)

        print("remote status =", resp.status_code)
        print("remote content-type =", resp.headers.get("content-type"))

        if resp.status_code != 200:
            raise HTTPException(status_code=404, detail="Remote packaging image not found")

        content_type = resp.headers.get("content-type", "image/png")
        return Response(content=resp.content, media_type=content_type)

    except HTTPException:
        raise
    except Exception as e:
        print("mockup fetch error =", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch packaging mockup: {str(e)}")