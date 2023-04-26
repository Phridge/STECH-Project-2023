# Farbsammlung für das gesamte Programm im Form von Klassen

class BlackWhite:   # klassisches achromatisches Farbschema
    color = (0, 0, 0)                   # Standard-Hintergrund
    border = (255, 255, 255)            # Standard-Border
    text = (255, 255, 255, 255)         # Standard-Text
    hover = (50, 50, 50)                # Hintergrund beim Hovern
    hover_border = (255, 255, 255)      # Border beim Hovern
    hover_text = (255, 255, 255, 255)   # Text beim Hovern
    click = (255, 255, 255)             # Hintergrund beim Klicken
    click_border = (255, 255, 255)      # Border beim Klicken
    click_text = (0, 0, 0, 255)         # Text beim Klicken
    img_hover = (150, 150, 150)         # Bilder beim Hovern
    img_click = (100, 100, 100)         # Bilder beim Klicken
    border_thickness = 2


class DarkPurple:   # Dunkles Farbschema, mit lila Akzenten
    color = (0, 0, 0)  # Standard-Hintergrund
    border = (175, 0, 255)  # Standard-Border
    text = (175, 0, 255, 255)  # Standard-Text
    hover = (150, 50, 200)  # Hintergrund beim Hovern
    hover_border = (175, 0, 255)  # Border beim Hovern
    hover_text = (0, 0, 0, 255)  # Text beim Hovern
    click = (100, 0, 150)  # Hintergrund beim Klicken
    click_border = (175, 0, 255)  # Border beim Klicken
    click_text = (200, 50, 255, 255)  # Text beim Klicken
    img_hover = (200, 150, 255)  # Bilder beim Hovern
    img_click = (175, 100, 255)  # Bilder beim Klicken
    border_thickness = 2


class Font1:
    header_font_size = 36
    font_size = 13
    font_name = "Arial"
