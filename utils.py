import random
import io
import httpx
import time
import logging
import os
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_random_profile_picture():
    """Fetch a random profile picture from thispersondoesnotexist.com with retries."""
    # DO NOT change this URL back to the root "https://thispersondoesnotexist.com/".
    # The root returns an HTML page with the image embedded in it (200 OK, not an image),
    # which makes Image.open fail with "cannot identify image file". The
    # /random-person.jpeg endpoint returns the raw JPEG, a new random face on every request.
    url = "https://thispersondoesnotexist.com/random-person.jpeg"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "image/jpeg,image/png,image/*;q=0.8,*/*;q=0.5",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    
    logger.info("Starting to fetch random profile picture from thispersondoesnotexist.com")
    for attempt in range(3):
        try:
            logger.info(f"Attempt {attempt + 1}: Sending GET request to {url}")
            # Wait longer (1 minute) for the response
            response = httpx.get(url, headers=headers, follow_redirects=True, timeout=60.0)
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                # Keep this decode check: a 200 response is not guaranteed to be an image,
                # and the diagnostic logging below is what exposed the HTML-vs-JPEG issue.
                try:
                    img = Image.open(io.BytesIO(response.content))
                    img.load()  # Fully decode now so a bad payload fails here, not later
                except Exception as e:
                    # A 200 that isn't an image is usually an anti-bot/challenge page
                    logger.error(
                        f"Attempt {attempt + 1}: 200 OK but body is not a decodable image "
                        f"(content-type={content_type!r}, {len(response.content)} bytes, "
                        f"starts with {response.content[:60]!r}): {e}"
                    )
                else:
                    logger.info(f"Successfully fetched random profile picture on attempt {attempt + 1}")
                    return img
            else:
                logger.warning(f"Attempt {attempt + 1} failed with status code: {response.status_code}")
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed with error: {e}")
        
        if attempt < 2:
            delay = 2 ** (attempt + 1)
            logger.info(f"Waiting {delay} seconds before next attempt...")
            time.sleep(delay)
            
    logger.error("Failed to fetch random profile picture after 3 attempts.")
    return None

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

def get_font(size: int, weight: str = "regular", display: bool = False):
    """
    Load the bundled Inter font (a close open-source match for Apple's SF Pro) at `size`, in
    `weight` ("regular", "medium" or "semibold"). `display` picks Inter Display, the cut with
    tighter spacing meant for larger text. If it can't be loaded, a standard system font is
    tried, falling back to the default font.
    """
    family = "InterDisplay" if display else "Inter"
    name = "SemiBold" if weight == "semibold" else weight.capitalize()
    path = os.path.join(FONT_DIR, f"{family}-{name}.ttf")
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        logger.warning(f"Could not load bundled font {path}, using system fonts")
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

def get_multiline_layout(draw: ImageDraw, text: str, max_width: int, max_height: int, initial_size: int, weight: str = "regular"):
    """
    Finds the best font size and wrapped text combination.
    Prioritizes wrapping at the initial size. Shrinks only if max_height is exceeded.
    """
    logger.debug(f"Calculating layout for text: '{text[:20]}...' initial_size: {initial_size}")
    size = initial_size
    while size >= 10:
        font = get_font(size, weight)
        wrapped_text = wrap_text(text, font, max_width)
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align="center")
        h = bbox[3] - bbox[1]
        w = bbox[2] - bbox[0]
        if h <= max_height:
            logger.debug(f"Found suitable layout: size {size}, width {w}, height {h}")
            return wrapped_text, font, w, h
        size -= 4
    
    logger.warning("Could not fit text within max_height even at small size. Using minimum size 10.")
    font = get_font(10, weight)
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


def _rounded_mask(size, box, radius, supersample=4):
    """Anti-aliased rounded-rectangle mask (radius >= half the shorter side gives a pill/circle)."""
    w, h = size
    mask = Image.new("L", (w * supersample, h * supersample), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [c * supersample for c in box], radius=max(radius, 0) * supersample, fill=255
    )
    return mask.resize((w, h), Image.LANCZOS)

def _scale_alpha(mask, alpha: int):
    return mask.point(lambda v: v * alpha // 255)

def draw_glass(img, box, radius, tint, border=(255, 255, 255, 160), border_width=2,
               highlight=70, shadow=(0, 0, 0, 40), shadow_blur=16, shadow_offset=8, backdrop_blur=12):
    """
    Composite a frosted-glass rounded rectangle onto an RGBA image, in place.

    Layers, bottom to top: soft drop shadow, blurred backdrop, translucent tint,
    a top-down white sheen, and a thin light rim. `tint`, `border` and `shadow` are RGBA.
    """
    x0, y0, x1, y1 = [int(round(c)) for c in box]
    pad = shadow_blur * 3 + shadow_offset
    rx0, ry0 = max(0, x0 - pad), max(0, y0 - pad)
    rx1, ry1 = min(img.width, x1 + pad), min(img.height, y1 + pad)
    size = (rx1 - rx0, ry1 - ry0)
    local = (x0 - rx0, y0 - ry0, x1 - rx0, y1 - ry0)

    mask = _rounded_mask(size, local, radius)
    original = img.crop((rx0, ry0, rx1, ry1))

    # Shadow, then swap the glass area for the blurred backdrop so the shadow doesn't show through it
    shadow_mask = _rounded_mask(size, (local[0], local[1] + shadow_offset, local[2], local[3] + shadow_offset), radius)
    shadow_mask = _scale_alpha(shadow_mask.filter(ImageFilter.GaussianBlur(shadow_blur)), shadow[3])
    shadow_layer = Image.new("RGBA", size, shadow[:3] + (0,))
    shadow_layer.putalpha(shadow_mask)
    region = Image.alpha_composite(original, shadow_layer)
    region.paste(original.filter(ImageFilter.GaussianBlur(backdrop_blur)), (0, 0), mask)

    tint_layer = Image.new("RGBA", size, tint[:3] + (0,))
    tint_layer.putalpha(_scale_alpha(mask, tint[3]))
    region = Image.alpha_composite(region, tint_layer)

    # Sheen: white fading from the top edge to about half way down
    box_w, box_h = local[2] - local[0], local[3] - local[1]
    sheen = Image.linear_gradient("L").transpose(Image.FLIP_TOP_BOTTOM).resize((box_w, max(1, box_h // 2)))
    sheen_full = Image.new("L", size, 0)
    sheen_full.paste(sheen, (local[0], local[1]))
    sheen_layer = Image.new("RGBA", size, (255, 255, 255, 0))
    sheen_layer.putalpha(_scale_alpha(ImageChops.multiply(sheen_full, mask), highlight))
    region = Image.alpha_composite(region, sheen_layer)

    # Rim: the mask minus an inset copy of itself
    inner = _rounded_mask(size, (local[0] + border_width, local[1] + border_width,
                                 local[2] - border_width, local[3] - border_width), radius - border_width)
    rim_layer = Image.new("RGBA", size, border[:3] + (0,))
    rim_layer.putalpha(_scale_alpha(ImageChops.subtract(mask, inner), border[3]))
    region = Image.alpha_composite(region, rim_layer)

    img.paste(region, (rx0, ry0))
