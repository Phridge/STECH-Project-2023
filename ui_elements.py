import pyglet
# Erweitert die Pyglet-Klassen, um Daraus Buttons, Banner und Formen zu machen


# Pyglet Rectangle wird erweitert um auszugeben wann gehovert und geklickt wird und einen Text anzuzeigen
class BorderedRectangleButton(pyglet.shapes.BorderedRectangle):
    def __init__(self, text, x, y, width, height, color_scheme, font_scheme, events, batch=None, group=None):
        pyglet.shapes.BorderedRectangle.__init__(self, x, y, width, height, color_scheme.border_thickness, color_scheme.color, color_scheme.border, batch=batch, group=None)
        self.label = pyglet.text.Label(text, batch=batch, font_name=font_scheme.font_name, font_size=font_scheme.font_size, color=color_scheme.text, anchor_x="center", anchor_y="center", x=x+width//2, y=y+height//2)

        def is_hovered(data): # wird aufgerufen um den Button an seinen aktuellen State anzupassen. Kann aufgerufen werden um den State zu checken
            mouse_x, mouse_y = data
            if x <= int(mouse_x) <= x+width and y <= int(mouse_y) <= y+height:
                self.color = color_scheme.hover
                self.border = color_scheme.hover_border
                self.label.color = color_scheme.hover_text
                return True
            else:
                self.color = color_scheme.color
                self.border = color_scheme.border
                self.label.color = color_scheme.text
                return False

        def button_clicked(data): # detected wenn der Button gedrückt wird.
            pass
            mouse_state, mouse_x, mouse_y, button = data # button zeigt den gedrückten knopf: Links=1, Rad=2, Rechts=4
            if mouse_state is True and button == 1 and x <= int(mouse_x) <= x+width and y <= int(mouse_y) <= y+height:
                self.color = color_scheme.click
                self.border = color_scheme.click_border
                self.label.color = color_scheme.click_text
                return True
            else:
                is_hovered((mouse_x, mouse_y))
                return False

        events.mouse.subscribe(is_hovered)
        events.mouse_button.subscribe(button_clicked)


# nicht klickbare Variante für Überschiften o.ä.
class BorderedRectangle(pyglet.shapes.BorderedRectangle):
    def __init__(self, text, x, y, width, height, color_scheme, font_scheme, batch=None, group=None):
        pyglet.shapes.BorderedRectangle.__init__(self, x, y, width, height, color_scheme.border_thickness, color_scheme.color, color_scheme.border, batch=batch, group=None)
        self.label = pyglet.text.Label(text, batch=batch, font_name=font_scheme.font_name, color=color_scheme.text ,font_size=font_scheme.font_size, anchor_x="center", anchor_y="center", x=x+width//2, y=y+height//2)


# Pyglet Sprite wird erwetert um Bilder klickbar machen zu können (nicht Image, da man das nicht skalieren kann)
class ClickableSprite(pyglet.sprite.Sprite):
    def __init__(self, path, x, y, width, height, color_scheme, events, batch=None):
        image = pyglet.image.load(path)
        pyglet.sprite.Sprite.__init__(self, image, x, y, z=1, batch=batch)
        self.scale_x = width / self.width # skaliert das Bild auf die angegebene Pixelzahl
        self.scale_y = height / self.height

        def is_hovered(data):  # wird aufgerufen um den Button an seinen aktuellen State anzupassen. Kann aufgerufen werden um den State zu checken
            mouse_x, mouse_y = data
            if x <= int(mouse_x) <= x + width and y <= int(mouse_y) <= y + height:
                self.color = color_scheme.img_hover
                return True
            else:
                self.color = (255,255,255)
                return False

        def button_clicked(data):  # detected wenn der Button gedrückt wird.
            pass
            mouse_state, mouse_x, mouse_y, button = data  # button zeigt den gedrückten knopf: Links=1, Rad=2, Rechts=4
            if mouse_state is True and button == 1 and x <= int(mouse_x) <= x + width and y <= int(mouse_y) <= y + height:
                self.color = color_scheme.img_click
                return True
            else:
                is_hovered((mouse_x, mouse_y))
                return False

        events.mouse.subscribe(is_hovered)
        events.mouse_button.subscribe(button_clicked)


# nicht klickbare Variante
class Sprite(pyglet.sprite.Sprite):
    def __init__(self, path, x, y, width, height, color_scheme,  batch=None):
        image = pyglet.image.load(path)
        pyglet.sprite.Sprite.__init__(self, image, x, y, z=1, batch=batch)
        self.scale_x = width / self.width # skaliert das Bild auf die angegebene Pixelzahl
        self.scale_y = height / self.height