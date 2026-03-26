import os
from PIL import Image, ImageDraw, ImageOps
from utils import create_gradient, get_font, wrap_text, get_multiline_layout

def linkedin_theme_1(request):
    # 1. Create Canvas
    width, height = 512, 512
    img = create_gradient(width, height)
    draw = ImageDraw.Draw(img)
    text_color = (240, 240, 240)
    margin = 35
    safe_width = width - (margin * 2)
    
    # 2. Pre-calculate Title and Subtitle Layouts
    title_data = None
    if request.title:
        title_data = get_multiline_layout(draw, request.title, safe_width, 240, 50)
    
    sub_data = None
    if request.subtitle:
        sub_data = get_multiline_layout(draw, request.subtitle, safe_width, 140, 26)
    
    # 3. Calculate Vertical Centering
    gap = 40
    total_text_height = 0
    if title_data:
        total_text_height += title_data[3]
    if title_data and sub_data:
        total_text_height += gap
    if sub_data:
        total_text_height += sub_data[3]
    
    # Starting Y to center the whole block
    start_y = (height - total_text_height) // 2
    
    # 4. Draw Header
    if request.header:
        header_font = get_font(14)
        header_text = wrap_text(request.header, header_font, safe_width // 2)
        draw.multiline_text((margin, margin), header_text, font=header_font, fill=text_color)
        
    # 5. Draw Title
    current_y = start_y
    if title_data:
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
    return img

def twitter_theme_1(request):
    """
    Twitter screenshot style theme.
    - Black background
    - Circular profile picture
    - Profile name (request.header), verified tick, handle (request.footer)
    - Title and subtitle left aligned
    """
    width, height = 512, 512
    img = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    margin = 40
    text_color = (255, 255, 255)  # White text
    secondary_text_color = (113, 118, 123)  # Twitter secondary gray
    
    # 1. Profile Picture
    profile_pic_size = 60
    profile_x, profile_y = margin, margin
    
    # Try to load profile.png, else use placeholder circle
    profile_path = "profile.png"
    if os.path.exists(profile_path):
        try:
            profile_img = Image.open(profile_path).convert("RGBA")
            profile_img = ImageOps.fit(profile_img, (profile_pic_size, profile_pic_size), centering=(0.5, 0.5))
            
            # Create circular mask
            mask = Image.new("L", (profile_pic_size, profile_pic_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, profile_pic_size, profile_pic_size), fill=255)
            
            img.paste(profile_img, (profile_x, profile_y), mask)
        except Exception:
            # Fallback to placeholder circle if image is invalid
            draw.ellipse((profile_x, profile_y, profile_x + profile_pic_size, profile_y + profile_pic_size), fill=(60, 60, 60))
    else:
        # Placeholder circle
        draw.ellipse((profile_x, profile_y, profile_x + profile_pic_size, profile_y + profile_pic_size), fill=(60, 60, 60))
        
    # 2. Header Row: Name, Verified Tick, Handle
    name_font = get_font(20)
    handle_font = get_font(18)
    
    current_x = profile_x + profile_pic_size + 15
    # Vertically center the text with the profile pic
    text_base_y = profile_y + (profile_pic_size // 2) - 10
    
    # Profile Name
    profile_name = request.header or "Profile Name"
    draw.text((current_x, text_base_y), profile_name, font=name_font, fill=text_color)
    name_width = draw.textlength(profile_name, font=name_font)
    current_x += name_width + 5
    
    # Verified Tick
    verified_path = "verified.png"
    if os.path.exists(verified_path):
        try:
            verified_img = Image.open(verified_path).convert("RGBA")
            # Resize tick to be roughly the size of the font
            tick_size = 20
            verified_img = verified_img.resize((tick_size, tick_size), resample=Image.LANCZOS)
            # Paste it a bit higher to align with text middle
            img.paste(verified_img, (int(current_x), int(text_base_y + 2)), verified_img)
            current_x += tick_size + 5
        except Exception:
            pass
            
    # User Handle
    handle_text = request.footer or "@user"
    draw.text((current_x, text_base_y), handle_text, font=handle_font, fill=secondary_text_color)
    
    # 3. Content: Title and Subtitle
    content_y = profile_y + profile_pic_size + 30
    safe_width = width - (margin * 2)
    content_font = get_font(28)
    
    if request.title:
        wrapped_title = wrap_text(request.title, content_font, safe_width)
        draw.multiline_text((margin, content_y), wrapped_title, font=content_font, fill=text_color, align="left")
        bbox = draw.multiline_textbbox((margin, content_y), wrapped_title, font=content_font, align="left")
        content_y = bbox[3] + 20
        
    if request.subtitle:
        wrapped_subtitle = wrap_text(request.subtitle, content_font, safe_width)
        draw.multiline_text((margin, content_y), wrapped_subtitle, font=content_font, fill=text_color, align="left")
        
    return img
