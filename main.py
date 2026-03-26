import io
from typing import Optional

from fastapi import FastAPI, Response
from pydantic import BaseModel
from themes import linkedin_theme_1

app = FastAPI(title="Social Media Image Generator")

class ImageRequest(BaseModel):
    header: Optional[str] = ""
    title: Optional[str] = ""
    subtitle: Optional[str] = ""
    footer: Optional[str] = ""
    theme: Optional[str] = "linkedin-theme-1"

@app.post("/generate")
async def generate_image(request: ImageRequest):
    if request.theme == "linkedin-theme-1":
        img = linkedin_theme_1(request)
    else:
        # Fallback or additional themes
        img = linkedin_theme_1(request)

    # Return image
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return Response(content=img_byte_arr.getvalue(), media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
