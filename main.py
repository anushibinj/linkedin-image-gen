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
    # Common font paths/names for different OS (Windows, Linux, macOS)
    font_names = [
        "arial.ttf", 
        "DejaVuSans.ttf", 
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "LiberationSans-Regular.ttf", 
        "Verdana.ttf"
    ]
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()

def get_fitted_font(draw: ImageDraw, text: str, max_width: int, initial_size: int):
    """Iteratively shrink font size until text fits within max_width."""
    size = initial_size
    font = get_font(size)
    
    # If text is empty, return initial font
    if not text:
        return font
        
    while size > 10:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        if text_width <= max_width:
            break
        size -= 2
        font = get_font(size)
    return font

def create_gradient(width: int, height: int):
    """Generate a random dark diagonal linear gradient."""
    # Ensure color1 and color2 are distinct enough to see the gradient
    color1 = (random.randint(5, 30), random.randint(5, 30), random.randint(5, 30))
    color2 = (random.randint(50, 90), random.randint(50, 90), random.randint(50, 90))
    
    base = Image.new("RGB", (width, height), color1)
    top = Image.new("RGB", (width, height), color2)
    
    # Create a small 2x2 mask for a diagonal gradient and scale it up
    mask = Image.new("L", (2, 2))
    mask.putpixel((0, 0), 0)    # Top-left
    mask.putpixel((1, 1), 255)  # Bottom-right
    mask.putpixel((0, 1), 128)  # Bottom-left
    mask.putpixel((1, 0), 128)  # Top-right
    
    # Resize to full canvas with BILINEAR to create a smooth diagonal transition
    mask = mask.resize((width, height), resample=Image.BILINEAR)
    
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
    safe_width = width - (margin * 2)
    
    # 2. Draw Header (Top-Left)
    if request.header:
        header_font = get_fitted_font(draw, request.header, safe_width // 2, 16)
        draw.text((margin, margin), request.header, font=header_font, fill=text_color)
        
    # 3. Draw Title (Centered)
    title_y = 200 # Slightly above middle
    if request.title:
        title_font = get_fitted_font(draw, request.title, safe_width, 50)
        bbox = draw.textbbox((0, 0), request.title, font=title_font)
        text_width = bbox[2] - bbox[0]
        title_x = (width - text_width) // 2
        draw.text((title_x, title_y), request.title, font=title_font, fill=text_color)
        title_height = bbox[3] - bbox[1]
    else:
        title_height = 0

    # 4. Draw Subtitle (Below Title, Centered)
    if request.subtitle:
        subtitle_font = get_fitted_font(draw, request.subtitle, safe_width, 26)
        bbox = draw.textbbox((0, 0), request.subtitle, font=subtitle_font)
        text_width = bbox[2] - bbox[0]
        sub_x = (width - text_width) // 2
        sub_y = title_y + title_height + 15 # 15px gap
        draw.text((sub_x, sub_y), request.subtitle, font=subtitle_font, fill=text_color)

    # 5. Draw Footer (Bottom-Right)
    if request.footer:
        # Footer is allowed up to 60% of width
        footer_font = get_fitted_font(draw, request.footer, int(width * 0.6), 16)
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
