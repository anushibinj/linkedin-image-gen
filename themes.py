from PIL import ImageDraw
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
