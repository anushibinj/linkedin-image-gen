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

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int):
    """Wrap text into multiple lines based on pixel width."""
    lines = []
    words = text.split()
    while words:
        line = ""
        while words:
            test_line = (line + " " + words[0]).strip()
            if font.getlength(test_line) <= max_width:
                line = test_line
                words.pop(0)
            else:
                break
        if not line:
            line = words.pop(0)
        lines.append(line)
    return "\n".join(lines)

def get_multiline_layout(draw: ImageDraw, text: str, max_width: int, max_height: int, initial_size: int):
    """
    Finds the best font size and wrapped text combination.
    Prioritizes wrapping at the initial size. Shrinks only if max_height is exceeded.
    """
    size = initial_size
    while size >= 10:
        font = get_font(size)
        wrapped_text = wrap_text(text, font, max_width)
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align="center")
        h = bbox[3] - bbox[1]
        w = bbox[2] - bbox[0]
        if h <= max_height:
            return wrapped_text, font, w, h
        size -= 4
    font = get_font(10)
    wrapped_text = wrap_text(text, font, max_width)
    bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align="center")
    return wrapped_text, font, bbox[2]-bbox[0], bbox[3]-bbox[1]

def create_gradient(width: int, height: int):
    """Generate a random dark diagonal linear gradient."""
    color1 = (random.randint(5, 30), random.randint(5, 30), random.randint(5, 30))
    color2 = (random.randint(50, 90), random.randint(50, 90), random.randint(50, 90))
    base = Image.new("RGB", (width, height), color1)
    top = Image.new("RGB", (width, height), color2)
    mask = Image.new("L", (2, 2))
    mask.putpixel((0, 0), 0)
    mask.putpixel((1, 1), 255)
    mask.putpixel((0, 1), 128)
    mask.putpixel((1, 0), 128)
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
    margin = 30
    safe_width = width - (margin * 2)
    
    # 2. Draw Header
    if request.header:
        header_font = get_font(16)
        if header_font.getlength(request.header) > safe_width // 2:
             header_text = wrap_text(request.header, header_font, safe_width // 2)
        else:
             header_text = request.header
        draw.multiline_text((margin, margin), header_text, font=header_font, fill=text_color)
        
    # 3. Draw Title
    title_y = 160
    if request.title:
        wrapped_title, title_font, title_w, title_h = get_multiline_layout(
            draw, request.title, safe_width, 220, 50
        )
        # Manually center horizontally
        title_x = (width - title_w) // 2
        draw.multiline_text(
            (title_x, title_y), 
            wrapped_title, 
            font=title_font, 
            fill=text_color, 
            align="center"
        )
        current_y = title_y + title_h + 20
    else:
        current_y = title_y

    # 4. Draw Subtitle
    if request.subtitle:
        wrapped_sub, sub_font, sub_w, sub_h = get_multiline_layout(
            draw, request.subtitle, safe_width, 120, 26
        )
        # Manually center horizontally
        sub_x = (width - sub_w) // 2
        draw.multiline_text(
            (sub_x, current_y), 
            wrapped_sub, 
            font=sub_font, 
            fill=text_color, 
            align="center"
        )

    # 5. Draw Footer
    if request.footer:
        footer_font = get_font(14)
        wrapped_footer = wrap_text(request.footer, footer_font, safe_width // 2)
        bbox = draw.multiline_textbbox((0, 0), wrapped_footer, font=footer_font, align="right")
        f_w = bbox[2] - bbox[0]
        f_h = bbox[3] - bbox[1]
        draw.multiline_text(
            (width - margin - f_w, height - margin - f_h), 
            wrapped_footer, 
            font=footer_font, 
            fill=text_color,
            align="right"
        )

    # 6. Return image
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return Response(content=img_byte_arr.getvalue(), media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
