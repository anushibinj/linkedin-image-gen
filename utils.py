import random
from PIL import Image, ImageDraw, ImageFont

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
