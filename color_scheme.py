# Farbsammlung für das gesamte Programm im Form von Klassen
import logging

from pyglet import resource, font


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


def add_font(font_name):
    if not font.have_font(font_name):
        resource.add_font('assets/fonts/' + font_name + '.ttf')
        font.load(font_name)
    return font_name


class Arial:
    font_name = "Arial"


class Minecraft:
    font_name = add_font("Minecraft")

