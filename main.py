import io
import os
from typing import Optional

from fastapi import FastAPI, Response
from pydantic import BaseModel
from themes import linkedin_theme_1, twitter_theme_1, ios_messages_theme_1

app = FastAPI(title="Social Media Image Generator")

DEFAULT_HANDLE = os.getenv("TWITTER_HANDLE", "@fastorial")

class ImageRequest(BaseModel):
    header: Optional[str] = ""
    title: Optional[str] = ""
    subtitle: Optional[str] = ""
    footer: Optional[str] = ""
    theme: Optional[str] = "linkedin-theme-1"

@app.post("/generate")
async def generate_image(request: ImageRequest):
    # Set default handle if footer is empty and theme is twitter-theme-1
    if request.theme == "twitter-theme-1" and not request.footer:
        request.footer = DEFAULT_HANDLE

    if request.theme == "linkedin-theme-1":
        img = linkedin_theme_1(request)
    elif request.theme == "twitter-theme-1":
        img = twitter_theme_1(request)
    elif request.theme == "ios-messages-1":
        img = ios_messages_theme_1(request)
    else:
        # Fallback
        img = linkedin_theme_1(request)

    # Return image
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return Response(content=img_byte_arr.getvalue(), media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
