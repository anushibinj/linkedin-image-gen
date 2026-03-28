import io
import os
import logging
from typing import Optional

from fastapi import FastAPI, Response
from pydantic import BaseModel
from themes import linkedin_theme_1, twitter_theme_1, ios_messages_theme_1

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    logger.info(f"Received image generation request for theme: {request.theme}")
    logger.debug(f"Request data: {request.model_dump()}")
    
    # Set default handle if footer is empty and theme is twitter-theme-1
    if request.theme == "twitter-theme-1" and not request.footer:
        logger.info(f"Using default handle for twitter theme: {DEFAULT_HANDLE}")
        request.footer = DEFAULT_HANDLE

    try:
        if request.theme == "linkedin-theme-1":
            img = linkedin_theme_1(request)
        elif request.theme == "twitter-theme-1":
            img = twitter_theme_1(request)
        elif request.theme == "ios-messages-1":
            img = ios_messages_theme_1(request)
        else:
            logger.warning(f"Unknown theme requested: {request.theme}. Falling back to linkedin-theme-1.")
            img = linkedin_theme_1(request)
    except Exception as e:
        logger.error(f"Error during image generation: {e}", exc_info=True)
        return Response(content="Error generating image", status_code=500)

    # Return image
    logger.debug("Saving image to byte array for response")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    logger.info("Successfully generated image and returning response")
    return Response(content=img_byte_arr.getvalue(), media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Social Media Image Generator server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
