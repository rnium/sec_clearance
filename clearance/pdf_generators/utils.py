from django.conf import settings
def get_fonts_css_txt(font_names):
    css_text = ""
    for font_name in font_names.keys():
        font_path = settings.BASE_DIR/f"clearance/pdf_generators/fonts/{font_names[font_name]}"
        css_text += f"""@font-face {{
                        font-family: {font_name};
                        src: url(file://{font_path});}}"""
    return css_text
