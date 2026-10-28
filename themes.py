import os
import logging
from PIL import Image, ImageDraw, ImageOps
from utils import draw_glass, create_gradient, get_font, wrap_text, get_multiline_layout, generate_random_profile_picture

logger = logging.getLogger(__name__)

SCALE_FACTOR = 2
BASE_SIZE = 512
SIZE = BASE_SIZE * SCALE_FACTOR

def linkedin_theme_1(request):
    logger.info("Generating image with theme: linkedin-theme-1")
    # 1. Create Canvas
    width, height = SIZE, SIZE
    logger.debug(f"Creating canvas of size {width}x{height}")
    img = create_gradient(width, height)
    draw = ImageDraw.Draw(img)
    text_color = (240, 240, 240)
    margin = 35 * SCALE_FACTOR
    safe_width = width - (margin * 2)
    
    # 2. Pre-calculate Title and Subtitle Layouts
    title_data = None
    if request.title:
        logger.debug("Calculating layout for title")
        title_data = get_multiline_layout(draw, request.title, safe_width, 240 * SCALE_FACTOR, 50 * SCALE_FACTOR)
    
    sub_data = None
    if request.subtitle:
        logger.debug("Calculating layout for subtitle")
        sub_data = get_multiline_layout(draw, request.subtitle, safe_width, 140 * SCALE_FACTOR, 26 * SCALE_FACTOR)
    
    # 3. Calculate Vertical Centering
    logger.debug("Calculating vertical centering")
    gap = 40 * SCALE_FACTOR
    total_text_height = 0
    if title_data:
        total_text_height += title_data[3]
    if title_data and sub_data:
        total_text_height += gap
    if sub_data:
        total_text_height += sub_data[3]
    
    start_y = (height - total_text_height) // 2
    
    # 4. Draw Header
    if request.header:
        logger.debug(f"Drawing header: {request.header}")
        header_font = get_font(14 * SCALE_FACTOR)
        header_text = wrap_text(request.header, header_font, safe_width // 2)
        draw.multiline_text((margin, margin), header_text, font=header_font, fill=text_color)
        
    # 5. Draw Title
    current_y = start_y
    if title_data:
        logger.debug("Drawing title")
        wrapped_title, title_font, title_w, title_h = title_data
        title_x = (width - title_w) // 2
        draw.multiline_text(
            (title_x, current_y), 
            wrapped_title, 
            font=title_font, 
            fill=text_color, 
            align="center"
        )
        current_y += title_h + gap

    # 6. Draw Subtitle
    if sub_data:
        logger.debug("Drawing subtitle")
        wrapped_sub, sub_font, sub_w, sub_h = sub_data
        sub_x = (width - sub_w) // 2
        draw.multiline_text(
            (sub_x, current_y), 
            wrapped_sub, 
            font=sub_font, 
            fill=text_color, 
            align="center"
        )

    # 7. Draw Footer
    if request.footer:
        logger.debug(f"Drawing footer: {request.footer}")
        footer_font = get_font(14 * SCALE_FACTOR)
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
    logger.info("Finished generating linkedin-theme-1 image")
    return img

def twitter_theme_1(request):
    logger.info("Generating image with theme: twitter-theme-1")
    width, height = SIZE, SIZE
    logger.debug(f"Creating canvas of size {width}x{height} (Black background)")
    img = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    margin = 40 * SCALE_FACTOR
    text_color = (255, 255, 255)
    secondary_text_color = (113, 118, 123)
    
    # 1. Profile Picture
    logger.debug("Handling profile picture")
    profile_pic_size = 60 * SCALE_FACTOR
    profile_x, profile_y = margin, margin
    draw_circular_profile(img, "profile.png", (profile_x, profile_y), profile_pic_size)
        
    # 2. Header Row: Name, Verified Tick, Handle
    logger.debug("Drawing header row (name, tick, handle)")
    name_font = get_font(20 * SCALE_FACTOR)
    handle_font = get_font(18 * SCALE_FACTOR)
    current_x = profile_x + profile_pic_size + 15 * SCALE_FACTOR
    text_base_y = profile_y + (profile_pic_size // 2) - 10 * SCALE_FACTOR
    
    profile_name = request.header or "Profile Name"
    draw.text((current_x, text_base_y), profile_name, font=name_font, fill=text_color)
    name_width = draw.textlength(profile_name, font=name_font)
    current_x += name_width + 5 * SCALE_FACTOR
    
    verified_path = "verified.png"
    if os.path.exists(verified_path):
        try:
            verified_img = Image.open(verified_path).convert("RGBA")
            tick_size = 20 * SCALE_FACTOR
            verified_img = verified_img.resize((int(tick_size), int(tick_size)), resample=Image.LANCZOS)
            img.paste(verified_img, (int(current_x), int(text_base_y + 2 * SCALE_FACTOR)), verified_img)
            current_x += tick_size + 5 * SCALE_FACTOR
        except Exception as e:
            logger.error(f"Error drawing verified tick: {e}")
            
    handle_text = request.footer or "@user"
    draw.text((current_x, text_base_y), handle_text, font=handle_font, fill=secondary_text_color)
    
    # 3. Content: Title and Subtitle
    logger.debug("Drawing main content (title and subtitle)")
    current_y = profile_y + profile_pic_size + 30 * SCALE_FACTOR
    safe_width = width - (margin * 2)
    content_font = get_font(28 * SCALE_FACTOR)
    
    if request.title:
        wrapped_title = wrap_text(request.title, content_font, safe_width)
        draw.multiline_text((margin, current_y), wrapped_title, font=content_font, fill=text_color, align="left")
        bbox = draw.multiline_textbbox((margin, current_y), wrapped_title, font=content_font, align="left")
        current_y = bbox[3] + 20 * SCALE_FACTOR
        
    if request.subtitle:
        wrapped_subtitle = wrap_text(request.subtitle, content_font, safe_width)
        draw.multiline_text((margin, current_y), wrapped_subtitle, font=content_font, fill=text_color, align="left")
        
    logger.info("Finished generating twitter-theme-1 image")
    return img

def draw_circular_profile(img, path_or_image, pos, size):
    """Utility to draw a circular profile picture from a path, Image object, or placeholder."""
    logger.debug(f"Drawing circular profile picture at {pos} with size {size}")
    draw = ImageDraw.Draw(img)
    x, y = pos
    profile_img = None
    
    if isinstance(path_or_image, Image.Image):
        logger.debug("Profile picture provided as Image object")
        profile_img = path_or_image
    elif isinstance(path_or_image, str):
        if os.path.exists(path_or_image):
            logger.debug(f"Loading profile picture from path: {path_or_image}")
            try:
                profile_img = Image.open(path_or_image).convert("RGBA")
            except Exception as e:
                logger.error(f"Error opening profile picture {path_or_image}: {e}")
        else:
            logger.debug(f"Profile picture path {path_or_image} does not exist")

    if profile_img:
        try:
            profile_img = profile_img.convert("RGBA")
            profile_img = ImageOps.fit(profile_img, (int(size), int(size)), centering=(0.5, 0.5))
            mask = Image.new("L", (int(size), int(size)), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, int(size), int(size)), fill=255)
            img.paste(profile_img, (int(x), int(y)), mask)
            logger.debug("Successfully drew circular profile picture")
            return
        except Exception as e:
            logger.error(f"Error processing profile image: {e}")
    
    logger.debug("Falling back to placeholder circle for profile picture")
    draw.ellipse((x, y, x + size, y + size), fill=(200, 200, 200))

def _text_pill(img, text, font, center_x, top, fill, glass, padding_x, padding_y):
    """Draw `text` on a glass pill whose top edge is at `top`. Returns the pill's box."""
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font)
    t_w, t_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    left = center_x - t_w / 2 - padding_x
    box = (left, top, left + t_w + padding_x * 2, top + t_h + padding_y * 2)
    draw_glass(img, box, (box[3] - box[1]) / 2, **glass)
    draw.text((left + padding_x - bbox[0], top + padding_y - bbox[1]), text, font=font, fill=fill)
    return box


def _ios_messages_theme(request, theme_name, colors):
    logger.info(f"Generating image with theme: {theme_name}")
    width, height = SIZE, SIZE
    logger.debug(f"Creating canvas of size {width}x{height} (background: {colors['background']})")
    img = Image.new("RGBA", (width, height), colors["background"] + (255,))

    # A large tinted glass panel sits on the background and holds everything else
    panel_inset = 20 * SCALE_FACTOR
    draw_glass(img, (panel_inset, panel_inset, width - panel_inset, height - panel_inset),
               radius=28 * SCALE_FACTOR, **colors["panel"])
    draw = ImageDraw.Draw(img)

    margin = panel_inset + 25 * SCALE_FACTOR
    safe_width = width - (margin * 2)
    bubble_max_width = int(safe_width * 0.7)
    profile_size = 35 * SCALE_FACTOR
    ring = 3 * SCALE_FACTOR
    pill_gap = panel_inset + 18 * SCALE_FACTOR

    def draw_avatar(source, xy):
        x, y = xy
        draw_glass(img, (x - ring, y - ring, x + profile_size + ring, y + profile_size + ring),
                   radius=profile_size, **colors["avatar_ring"])
        draw_circular_profile(img, source, xy, profile_size)

    # 1. Header (Receiver Name)
    current_y = margin + 20 * SCALE_FACTOR
    if request.header:
        logger.debug(f"Drawing header (receiver name): {request.header}")
        header_font = get_font(18 * SCALE_FACTOR)
        header_box = _text_pill(img, request.header, header_font, width / 2, pill_gap,
                                colors["header_text"], colors["pill"], 18 * SCALE_FACTOR, 9 * SCALE_FACTOR)
        current_y = header_box[3] + 30 * SCALE_FACTOR

    content_font = get_font(20 * SCALE_FACTOR)

    def draw_bubble(text, x, y, fill, text_fill):
        wrapped_text = wrap_text(text, content_font, bubble_max_width - 30 * SCALE_FACTOR)
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=content_font)
        bubble_w = bbox[2] - bbox[0] + 30 * SCALE_FACTOR
        bubble_h = bbox[3] - bbox[1] + 30 * SCALE_FACTOR
        bubble_x = x(bubble_w)
        draw_glass(img, (bubble_x, y, bubble_x + bubble_w, y + bubble_h), radius=18 * SCALE_FACTOR, **fill)
        draw.multiline_text((bubble_x + 15 * SCALE_FACTOR, y + 10 * SCALE_FACTOR), wrapped_text,
                            font=content_font, fill=text_fill)
        return bubble_h

    # 2. Sender Message (Title) -> Right Aligned
    if request.title:
        logger.debug(f"Drawing sender message bubble: {request.title[:20]}...")
        bubble_h = draw_bubble(request.title,
                               lambda w: width - margin - profile_size - 10 * SCALE_FACTOR - w,
                               current_y, colors["sender_bubble"], colors["sender_text"])
        draw_avatar("profile.png", (width - margin - profile_size, current_y + bubble_h - profile_size))
        current_y += bubble_h + 30 * SCALE_FACTOR

    # 3. Receiver Message (Subtitle) -> Left Aligned
    if request.subtitle:
        logger.debug(f"Drawing receiver message bubble: {request.subtitle[:20]}...")
        bubble_h = draw_bubble(request.subtitle,
                               lambda w: margin + profile_size + 10 * SCALE_FACTOR,
                               current_y, colors["receiver_bubble"], colors["receiver_text"])

        logger.info("Fetching receiver profile picture")
        receiver_img = generate_random_profile_picture()
        if receiver_img is None:
            logger.info("Falling back to profile_receiver.png for receiver profile")
            receiver_img = "profile_receiver.png"

        draw_avatar(receiver_img, (margin, current_y + bubble_h - profile_size))

    # 4. Footer
    if request.footer:
        logger.debug(f"Drawing footer: {request.footer}")
        footer_font = get_font(12 * SCALE_FACTOR)
        pad_x, pad_y = 14 * SCALE_FACTOR, 7 * SCALE_FACTOR
        bbox = draw.textbbox((0, 0), request.footer, font=footer_font)
        pill_w, pill_h = bbox[2] - bbox[0] + pad_x * 2, bbox[3] - bbox[1] + pad_y * 2
        _text_pill(img, request.footer, footer_font, width - margin - pill_w / 2,
                   height - pill_gap - pill_h, colors["footer_text"], colors["pill"], pad_x, pad_y)

    logger.info(f"Finished generating {theme_name} image")
    return img.convert("RGB")


def ios_messages_theme_1(request):
    """iOS Messages, dark mode."""
    return _ios_messages_theme(request, "ios-messages-1", {
        "background": (0, 0, 0),
        "panel": {"tint": (90, 90, 98, 90), "border": (255, 255, 255, 50),
                  "highlight": 22, "shadow": (0, 0, 0, 0)},
        "pill": {"tint": (120, 120, 128, 80), "border": (255, 255, 255, 60),
                 "highlight": 30, "shadow": (0, 0, 0, 80), "shadow_blur": 8, "shadow_offset": 4},
        "avatar_ring": {"tint": (255, 255, 255, 60), "border": (255, 255, 255, 90), "border_width": 2,
                        "highlight": 40, "shadow": (0, 0, 0, 90), "shadow_blur": 8, "shadow_offset": 4},
        "header_text": (255, 255, 255),
        "sender_bubble": {"tint": (0, 122, 255, 200), "border": (255, 255, 255, 90),
                          "highlight": 60, "shadow": (0, 60, 160, 110)},
        "sender_text": (255, 255, 255),
        "receiver_bubble": {"tint": (150, 150, 160, 80), "border": (255, 255, 255, 70),
                            "highlight": 40, "shadow": (0, 0, 0, 100)},
        "receiver_text": (255, 255, 255),
        "footer_text": (170, 175, 180),
    })


def ios_messages_theme_2_light_mode(request):
    """iOS Messages, light mode."""
    return _ios_messages_theme(request, "ios-messages-2-light-mode", {
        "background": (255, 255, 255),      # #FFFFFF
        "panel": {"tint": (205, 208, 216, 130), "border": (255, 255, 255, 230),
                  "highlight": 90, "shadow": (40, 50, 80, 45), "shadow_blur": 20, "shadow_offset": 8},
        "pill": {"tint": (255, 255, 255, 120), "border": (255, 255, 255, 230),
                 "highlight": 80, "shadow": (40, 50, 80, 40), "shadow_blur": 8, "shadow_offset": 3},
        "avatar_ring": {"tint": (255, 255, 255, 150), "border": (255, 255, 255, 240), "border_width": 2,
                        "highlight": 90, "shadow": (40, 50, 80, 55), "shadow_blur": 8, "shadow_offset": 3},
        "header_text": (0, 0, 0),           # #000000
        "sender_bubble": {"tint": (65, 178, 251, 190), "border": (255, 255, 255, 200),
                          "highlight": 90, "shadow": (30, 120, 200, 80), "shadow_blur": 10, "shadow_offset": 4},
        "sender_text": (255, 255, 255),
        "receiver_bubble": {"tint": (255, 255, 255, 150), "border": (255, 255, 255, 230),
                            "highlight": 90, "shadow": (40, 50, 80, 45), "shadow_blur": 10, "shadow_offset": 4},
        "receiver_text": (30, 30, 30),      # #1E1E1E
        "footer_text": (110, 112, 118),
    })
