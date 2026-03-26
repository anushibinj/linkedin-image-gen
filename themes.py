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
    - Circular profile picture (placeholder if not found)
    - User handle next to profile pic
    - Title and subtitle left aligned
    """
    width, height = 512, 512
    img = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    margin = 40
    text_color = (255, 255, 255)  # White text
    secondary_text_color = (113, 118, 123)  # Twitter dark mode secondary gray
    
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
        
    # 2. User handle / ID
    handle_font = get_font(20)
    handle_x = profile_x + profile_pic_size + 15
    handle_y = profile_y + (profile_pic_size // 2) - 12
    draw.text((handle_x, handle_y), request.user_handle, font=handle_font, fill=text_color)
    
    # 3. Title (Paragraph 1)
    current_y = profile_y + profile_pic_size + 30
    safe_width = width - (margin * 2)
    
    if request.title:
        title_font = get_font(28)
        wrapped_title = wrap_text(request.title, title_font, safe_width)
        draw.multiline_text((margin, current_y), wrapped_title, font=title_font, fill=text_color, align="left")
        
        # Calculate height of title to offset subtitle
        bbox = draw.multiline_textbbox((margin, current_y), wrapped_title, font=title_font, align="left")
        current_y = bbox[3] + 20
        
    # 4. Subtitle (Paragraph 2)
    if request.subtitle:
        subtitle_font = get_font(22)
        wrapped_subtitle = wrap_text(request.subtitle, subtitle_font, safe_width)
        draw.multiline_text((margin, current_y), wrapped_subtitle, font=subtitle_font, fill=secondary_text_color, align="left")
        
    return img
