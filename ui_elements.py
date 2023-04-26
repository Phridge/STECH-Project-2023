import pyglet
# Erweitert die Pyglet-Klassen, um daraus Buttons, Banner und Formen zu machen


# Pyglet Rectangle wird erweitert um auszugeben wann gehovert und geklickt wird und einen Text anzuzeigen
class BorderedRectangleButton(pyglet.shapes.Rectangle):  # pyglet.BorderedRectangle wird nicht genutzt, da die Border Standardmäßig mit OpenGL-Gradienten umgesetzt ist --> nicht erwünscht
    def __init__(self, text,
                 x, y, width, height,  # alle Angaben in %
                 color_scheme, font_scheme, events, batch=None, group=None):

        # konvertiert die Prozentangaben zu Pixeln
        x_px, y_px, width_px, height_px = Refactor.percent_to_pixel(x, y, width, height, events.size.value)

        # zeichnet ein Rechteck in den Hintergrund, welches die Border ergibt
        self.borderRectangle = pyglet.shapes.Rectangle(x_px, y_px, width_px, height_px,
                                                       color_scheme.border,  # Style wird mitgegeben
                                                       batch=batch, group=None)

        # Zeichnet das Rechteck und den Text
        pyglet.shapes.Rectangle.__init__(self,
                                         x_px + color_scheme.border_thickness,
                                         y_px + color_scheme.border_thickness,
                                         width_px - 2 * color_scheme.border_thickness,
                                         height_px - 2 * color_scheme.border_thickness,
                                         color_scheme.color,  # Style wird mitgegeben
                                         batch=batch, group=None)

        self.label = pyglet.text.Label(text, x=x_px+width_px//2, y=y_px+height_px//2,  # Text wird in die Mitte des Buttons gezeichnet
                                       anchor_x="center", anchor_y="center",  # Text wird in die Mitte des Buttons gezeichnet
                                       batch=batch, font_name=font_scheme.font_name, font_size=font_scheme.font_size, color=color_scheme.text)

        def is_hovered(data):  # wird aufgerufen um den Button an seinen aktuellen State anzupassen. Kann aufgerufen werden um den State zu checken
            mouse_x, mouse_y, buttons = data  # buttons gibt an welche Maustasten gedrückt sind
            if buttons is False and x_px <= int(mouse_x) <= x_px+width_px and y_px <= int(mouse_y) <= y_px+height_px:  # testet ob Maus über dem Button ist, falls ja wird er gefärbt
                self.color = color_scheme.hover
                self.borderRectangle.color = color_scheme.hover_border
                self.label.color = color_scheme.hover_text
                return True
            elif buttons is False:  # elif verhindert, dass gehaltene Knöpfe überschrieben werden
                self.color = color_scheme.color
                self.borderRectangle.color = color_scheme.border
                self.label.color = color_scheme.text
                return False

        def button_clicked(data):  # detected wenn der Button gedrückt wird.
            mouse_state, mouse_x, mouse_y, button = data  # button zeigt den gedrückten knopf: Links=1, Rad=2, Rechts=4
            if mouse_state is True and button == 1 and x_px <= int(mouse_x) <= x_px+width_px and y_px <= int(mouse_y) <= y_px+height_px:
                self.color = color_scheme.click
                self.borderRectangle.color = color_scheme.click_border
                self.label.color = color_scheme.click_text
                return True
            else:  # falls nicht geclickt wird wird getestet ob gehovert wird
                is_hovered((mouse_x, mouse_y, mouse_state))
                return False

        events.mouse.subscribe(is_hovered)
        events.mouse_button.subscribe(button_clicked)


# nicht klickbare Variante für Überschiften o.ä.
class BorderedRectangle(pyglet.shapes.Rectangle): # pyglet.BorderedRectangle wird nicht genutzt, da die Border Standardmäßig mit OpenGL-Gradienten umgesetzt ist --> nicht erwünscht
    def __init__(self, text,
                 x, y, width, height,  # alle Angaben in %
                 color_scheme, font_scheme, events, batch=None, group=None):

        # konvertiert die Prozentangaben zu Pixeln
        x_px, y_px, width_px, height_px = Refactor.percent_to_pixel(x, y, width, height, events.size.value)

        # zeichnet ein Rechteck in den Hintergrund, welches die Border ergibt
        self.borderRectangle = pyglet.shapes.Rectangle(x_px, y_px, width_px, height_px,
                                                       color_scheme.border,  # Style wird mitgegeben
                                                       batch=batch, group=None)

        # Zeichnet das Rechteck und den Text
        pyglet.shapes.Rectangle.__init__(self,
                                         x_px + color_scheme.border_thickness,
                                         y_px + color_scheme.border_thickness,
                                         width_px - 2 * color_scheme.border_thickness,
                                         height_px - 2 * color_scheme.border_thickness,
                                         color_scheme.color,  # Style wird mitgegeben
                                         batch=batch, group=None)

        self.label = pyglet.text.Label(text, x=x_px+width_px//2, y=y_px+height_px//2,  # Text wird in die Mitte des Buttons gezeichnet
                                       anchor_x="center", anchor_y="center",  # Text wird in die Mitte des Buttons gezeichnet
                                       batch=batch, font_name=font_scheme.font_name, font_size=font_scheme.font_size, color=color_scheme.text)


# Pyglet Sprite wird erweitert um Bilder klickbar machen zu können (nicht reines Image, da man das nicht skalieren kann)
class ClickableSprite(pyglet.sprite.Sprite):
    def __init__(self, path,
                 x, y, width, height,  # alle Angaben in %
                 color_scheme, events, batch=None):

        # konvertiert die Prozentangaben zu Pixeln
        x_px, y_px, width_px, height_px = Refactor.percent_to_pixel(x, y, width, height, events.size.value)

        # zeichnet das Bild in der richtigen Größe
        image = pyglet.image.load(path)
        pyglet.sprite.Sprite.__init__(self, image, x_px, y_px, batch=batch)
        self.scale_x = width_px / self.width  # skaliert das Bild auf die angegebene Pixelzahl
        self.scale_y = height_px / self.height

        def is_hovered(data):  # wird aufgerufen um den Button an seinen aktuellen State anzupassen. Kann aufgerufen werden um den State zu checken
            mouse_x, mouse_y, buttons = data  # buttons gibt an welche Maustasten gedrückt sind
            if buttons is False and x_px <= int(mouse_x) <= x_px+width_px and y_px <= int(mouse_y) <= y_px+height_px: # testet ob Maus über dem Button ist, falls ja wird er gefärbt
                self.color = color_scheme.img_hover
                return True
            elif buttons is False:  # elif verhindert, dass gehaltene Knöpfe überschrieben werden
                self.color = (255, 255, 255)  # Bild ist standardmäßig normal
                return False

        def button_clicked(data):  # detected wenn der Button gedrückt wird.
            mouse_state, mouse_x, mouse_y, button = data  # button zeigt den gedrückten knopf: Links=1, Rad=2, Rechts=4
            if mouse_state is True and button == 1 and x_px <= int(mouse_x) <= x_px+width_px and y_px <= int(mouse_y) <= y_px+height_px:
                self.color = color_scheme.img_click
                return True
            else:  # falls nicht geclickt wird wird getestet ob gehovert wird
                is_hovered((mouse_x, mouse_y, mouse_state))
                return False

        events.mouse.subscribe(is_hovered)
        events.mouse_button.subscribe(button_clicked)


# nicht klickbare Variante
class Sprite(pyglet.sprite.Sprite):
    def __init__(self, path,
                 x, y, width, height,  # alle Angaben in %
                 events, batch=None):

        # konvertiert die Prozentangaben zu Pixeln
        x_px, y_px, width_px, height_px = Refactor.percent_to_pixel(x, y, width, height, events.size.value)

        image = pyglet.image.load(path)
        pyglet.sprite.Sprite.__init__(self, image, x_px, y_px, batch=batch)
        self.scale_x = width_px / self.width  # skaliert das Bild auf die angegebene Pixelzahl
        self.scale_y = height_px / self.height


# Pyglet Sprite wird erweitert um Bilder klickbar machen zu können (nicht reines Image, da man das nicht skalieren kann)
class BorderedClickableSprite(pyglet.sprite.Sprite):
    def __init__(self, path,
                 x, y, width, height,  # alle Angaben in %
                 color_scheme, events, batch=None):

        # konvertiert die Prozentangaben zu Pixeln
        x_px, y_px, width_px, height_px = Refactor.percent_to_pixel(x, y, width, height, events.size.value)

        # zeichnet ein Rechteck in den Hintergrund, welches die Border ergibt
        self.borderRectangle = pyglet.shapes.Rectangle(x_px, y_px, width_px, height_px,
                                                       color_scheme.border,  # Style wird mitgegeben
                                                       batch=batch, group=None)

        image = pyglet.image.load(path)
        pyglet.sprite.Sprite.__init__(self, image,
                                      x_px + color_scheme.border_thickness,
                                      y_px + color_scheme.border_thickness, batch=batch)
        self.scale_x = (
                                   width_px - 2 * color_scheme.border_thickness) / self.width  # skaliert das Bild auf die angegebene Pixelzahl
        self.scale_y = (height_px - 2 * color_scheme.border_thickness) / self.height

        def is_hovered(data):  # wird aufgerufen um den Button an seinen aktuellen State anzupassen. Kann aufgerufen werden um den State zu checken
            mouse_x, mouse_y, buttons = data  # buttons gibt an welche Maustasten gedrückt sind
            if buttons is False and x_px <= int(mouse_x) <= x_px+width_px and y_px <= int(mouse_y) <= y_px+height_px: # testet ob Maus über dem Button ist, falls ja wird er gefärbt
                self.color = color_scheme.img_hover
                self.borderRectangle.color = color_scheme.hover_border
                return True
            elif buttons is False:  # elif verhindert, dass gehaltene Knöpfe überschrieben werden
                self.color = (255, 255, 255)  # Bild ist standardmäßig normal
                self.borderRectangle.color = color_scheme.border
                return False

        def button_clicked(data):  # detected wenn der Button gedrückt wird.
            mouse_state, mouse_x, mouse_y, button = data  # button zeigt den gedrückten knopf: Links=1, Rad=2, Rechts=4
            if mouse_state is True and button == 1 and x_px <= int(mouse_x) <= x_px+width_px and y_px <= int(mouse_y) <= y_px+height_px:
                self.color = color_scheme.img_click
                self.borderRectangle.color = color_scheme.click_border
                return True
            else:  # falls nicht geclickt wird wird getestet ob gehovert wird
                is_hovered((mouse_x, mouse_y, mouse_state))
                return False

        events.mouse.subscribe(is_hovered)
        events.mouse_button.subscribe(button_clicked)


class BorderedSprite(pyglet.sprite.Sprite):
    def __init__(self, path,
                 x, y, width, height,  # alle Angaben in %
                 color_scheme, events, batch=None):

        # konvertiert die Prozentangaben zu Pixeln
        x_px, y_px, width_px, height_px = Refactor.percent_to_pixel(x, y, width, height, events.size.value)

        # zeichnet ein Rechteck in den Hintergrund, welches die Border ergibt
        self.borderRectangle = pyglet.shapes.Rectangle(x_px, y_px, width_px, height_px,
                                                       color_scheme.border,  # Style wird mitgegeben
                                                       batch=batch, group=None)

        image = pyglet.image.load(path)
        pyglet.sprite.Sprite.__init__(self, image,
                                      x_px + color_scheme.border_thickness,
                                      y_px + color_scheme.border_thickness, batch=batch)
        self.scale_x = (width_px - 2 * color_scheme.border_thickness) / self.width  # skaliert das Bild auf die angegebene Pixelzahl
        self.scale_y = (height_px - 2 * color_scheme.border_thickness) / self.height


class Gif(pyglet.sprite.Sprite):  # lädt ein Gif
    def __init__(self, path,
                 x, y, width, height,  # alle Angaben in %
                 color_scheme, events, batch=None):

        # konvertiert die Prozentangaben zu Pixeln
        x_px, y_px, width_px, height_px = Refactor.percent_to_pixel(x, y, width, height, events.size.value)

        # zeichnet ein Rechteck in den Hintergrund, welches die Border ergibt
        self.borderRectangle = pyglet.shapes.Rectangle(x_px, y_px, width_px, height_px,
                                                       color_scheme.border,  # Style wird mitgegeben
                                                       batch=batch, group=None)

        image = pyglet.image.load_animation(path)
        pyglet.sprite.Sprite.__init__(self, image,
                                      x_px + color_scheme.border_thickness,
                                      y_px + color_scheme.border_thickness, batch=batch)
        self.scale_x = (width_px - 2 * color_scheme.border_thickness) / self.width  # skaliert das Bild auf die angegebene Pixelzahl
        self.scale_y = (height_px - 2 * color_scheme.border_thickness) / self.height


# Klasse, die die Umrechnung von Prozent in Pixel ermöglicht
class Refactor:
    @classmethod
    def percent_to_pixel(cls, x, y, width, height, window_data):
        # konvertiert die Prozentangaben zu Pixeln
        screen_width, screen_height = window_data
        x_px = x * screen_width // 100
        y_px = y * screen_height // 100
        width_px = width * screen_width // 100
        height_px = height * screen_height // 100
        return x_px, y_px, width_px, height_px
