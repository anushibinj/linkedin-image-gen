import io
import random
from typing import Optional

from fastapi import FastAPI, Response
from pydantic import BaseModel
from PIL import Image, ImageDraw, ImageFont

app = FastAPI(title="Social Media Image Generator")

class ImageRequest(BaseModel):
    header: Optional[str] = ""
    title: Optional[str] = ""
    subtitle: Optional[str] = ""
    footer: Optional[str] = ""

def get_font(size: int):
    """Attempt to load a standard font, fallback to default if not found."""
    try:
        # Common font paths for different OS
        font_names = ["arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf", "Verdana.ttf"]
        for name in font_names:
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                continue
        return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()

def create_gradient(width: int, height: int):
    """Generate a random dark linear gradient."""
    color1 = (random.randint(10, 80), random.randint(10, 80), random.randint(10, 80))
    color2 = (random.randint(10, 80), random.randint(10, 80), random.randint(10, 80))
    
    base = Image.new("RGB", (width, height), color1)
    top = Image.new("RGB", (width, height), color2)
    mask = Image.new("L", (width, height))
    
    # Create vertical gradient mask
    for y in range(height):
        mask.putpixel((0, y), int(255 * (y / height)))
    mask = mask.resize((width, height))
    
    base.paste(top, (0, 0), mask)
    return base

@app.post("/generate")
async def generate_image(request: ImageRequest):
    # 1. Create Canvas
    width, height = 512, 512
    img = create_gradient(width, height)
    draw = ImageDraw.Draw(img)
    
    text_color = (240, 240, 240)
    margin = 20
    
    # 2. Draw Header (Top-Left)
    if request.header:
        header_font = get_font(16)
        draw.text((margin, margin), request.header, font=header_font, fill=text_color)
        
    # 3. Draw Title (Centered)
    title_font = get_font(50)
    title_y = 200 # Slightly above middle
    if request.title:
        # Calculate horizontal center
        bbox = draw.textbbox((0, 0), request.title, font=title_font)
        text_width = bbox[2] - bbox[0]
        title_x = (width - text_width) // 2
        draw.text((title_x, title_y), request.title, font=title_font, fill=text_color)
        
        # Update title height for subtitle positioning
        title_height = bbox[3] - bbox[1]
    else:
        title_height = 0

    # 4. Draw Subtitle (Below Title, Centered)
    if request.subtitle:
        subtitle_font = get_font(26)
        bbox = draw.textbbox((0, 0), request.subtitle, font=subtitle_font)
        text_width = bbox[2] - bbox[0]
        sub_x = (width - text_width) // 2
        sub_y = title_y + title_height + 15 # 15px gap
        draw.text((sub_x, sub_y), request.subtitle, font=subtitle_font, fill=text_color)

    # 5. Draw Footer (Bottom-Right)
    if request.footer:
        footer_font = get_font(16)
        bbox = draw.textbbox((0, 0), request.footer, font=footer_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        footer_x = width - text_width - margin
        footer_y = height - text_height - margin
        draw.text((footer_x, footer_y), request.footer, font=footer_font, fill=text_color)

    # 6. Return raw binary image
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return Response(content=img_byte_arr.getvalue(), media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
