import random
import io
import httpx
import time
import logging
from PIL import Image, ImageDraw, ImageFont

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_random_profile_picture():
    """Fetch a random profile picture from thispersondoesnotexist.com with retries."""
    url = "https://thispersondoesnotexist.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    logger.info("Starting to fetch random profile picture from thispersondoesnotexist.com")
    for attempt in range(3):
        try:
            logger.info(f"Attempt {attempt + 1}: Sending GET request to {url}")
            # Wait longer (1 minute) for the response
            response = httpx.get(url, headers=headers, follow_redirects=True, timeout=60.0)
            if response.status_code == 200:
                logger.info(f"Successfully fetched random profile picture on attempt {attempt + 1}")
                return Image.open(io.BytesIO(response.content))
            else:
                logger.warning(f"Attempt {attempt + 1} failed with status code: {response.status_code}")
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed with error: {e}")
        
        if attempt < 2:
            logger.info("Waiting 60 seconds before next attempt...")
            time.sleep(60)
            
    logger.error("Failed to fetch random profile picture after 3 attempts.")
    return None

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
            font = ImageFont.truetype(name, size)
            logger.debug(f"Successfully loaded font: {name} with size {size}")
            return font
        except OSError:
            continue
    logger.warning(f"Could not find any standard fonts. Falling back to default font with size {size}")
    return ImageFont.load_default()

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int):
    """Wrap text into multiple lines based on pixel width."""
    logger.debug(f"Wrapping text: '{text[:20]}...' with max_width: {max_width}")
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
    result = "\n".join(lines)
    logger.debug(f"Text wrapped into {len(lines)} lines")
    return result

def get_multiline_layout(draw: ImageDraw, text: str, max_width: int, max_height: int, initial_size: int):
    """
    Finds the best font size and wrapped text combination.
    Prioritizes wrapping at the initial size. Shrinks only if max_height is exceeded.
    """
    logger.debug(f"Calculating layout for text: '{text[:20]}...' initial_size: {initial_size}")
    size = initial_size
    while size >= 10:
        font = get_font(size)
        wrapped_text = wrap_text(text, font, max_width)
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align="center")
        h = bbox[3] - bbox[1]
        w = bbox[2] - bbox[0]
        if h <= max_height:
            logger.debug(f"Found suitable layout: size {size}, width {w}, height {h}")
            return wrapped_text, font, w, h
        size -= 4
    
    logger.warning("Could not fit text within max_height even at small size. Using minimum size 10.")
    font = get_font(10)
    wrapped_text = wrap_text(text, font, max_width)
    bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align="center")
    return wrapped_text, font, bbox[2]-bbox[0], bbox[3]-bbox[1]

def create_gradient(width: int, height: int):
    """Generate a random dark diagonal linear gradient."""
    logger.debug(f"Creating random gradient of size {width}x{height}")
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
