from reactivex.subject import Subject
import pyglet
# Erweitert die Pyglet-Klassen, um daraus Buttons, Banner und Formen zu machen


class BorderedRectangleButton:  # Es wird keine Klasse erweitert, damit man die Objekte in der Runtime neu zeichnen kann
    def __init__(self, text,
                 x, y, width, height,  # alle Angaben in %
                 color_scheme, font_scheme, font_size,  # für Aussehen
                 events,  # die events aus game.py werden mitgegeben, auf Veränderungen zu reagieren
                 sublist,  # Liste an Subscriptions des aktuellen Controllers
                 batch=None, group=None):  # Batch ermöglicht, dass alles gleichzeitig gerendert wird. Dadurch läuft das Programm effizienter

        # konvertiert die Prozentangaben zu Pixeln in Abhängigkeit der Fenstergröße
        x_px, y_px, width_px, height_px = Refactor.percent_to_pixel(x, y, width, height, events.size.value)

        # zeichnet ein Rechteck in den Hintergrund, welches die Border ergibt
        self.borderRectangle = pyglet.shapes.Rectangle(x_px, y_px, width_px, height_px,
                                                       color_scheme.border,  # Style wird mitgegeben
                                                       batch=batch, group=None)

        # Zeichnet das Rechteck
        self.rectangle = pyglet.shapes.Rectangle(x_px + color_scheme.border_thickness,
                                                 y_px + color_scheme.border_thickness,
                                                 width_px - 2 * color_scheme.border_thickness,
                                                 height_px - 2 * color_scheme.border_thickness,
                                                 color_scheme.color,  # Style wird mitgegeben
                                                 batch=batch, group=None)

        # Zeichnet den Text in die Mitte des Rechteckes
        self.label = pyglet.text.Label(text, x=x_px + width_px // 2, y=y_px + height_px // 2,
                                       # Text wird in die Mitte des Buttons gezeichnet
                                       anchor_x="center", anchor_y="center",
                                       # Text wird in die Mitte des Buttons gezeichnet
                                       batch=batch, font_name=font_scheme.font_name,
                                       font_size=width_px // (100 // font_size), color=color_scheme.text)


        def is_hovered(data):  # wird aufgerufen um den Button visuell anzupassen, falls er gehovert wird
            mouse_x, mouse_y, buttons = data  # buttons zeigt den gedrückten knopf: Links=1, Rad=2, Rechts=4
            if buttons is False and self.x_px <= int(mouse_x) <= self.x_px+self.width_px and self.y_px <= int(mouse_y) <= self.y_px+self.height_px:  # testet ob Maus über dem Button ist, falls ja wird er gefärbt
                self.rectangle.color = color_scheme.hover
                self.borderRectangle.color = color_scheme.hover_border
                self.label.color = color_scheme.hover_text
                return True
            elif buttons is False:  # elif verhindert, dass gehaltene Knöpfe überschrieben werden
                self.rectangle.color = color_scheme.color
                self.borderRectangle.color = color_scheme.border
                self.label.color = color_scheme.text
                return False

        def button_clicked(data):  # wird aufgerufen um den Button anzupassen, falls er geklickt wird
            mouse_state, mouse_x, mouse_y, buttons = data  # buttons zeigt den gedrückten knopf: Links=1, Rad=2, Rechts=4
            if mouse_state is True and buttons == 1 and self.x_px <= int(mouse_x) <= self.x_px+self.width_px and self.y_px <= int(mouse_y) <= self.y_px+self.height_px:
                self.rectangle.color = color_scheme.click
                self.borderRectangle.color = color_scheme.click_border
                self.label.color = color_scheme.click_text
                self.clicked.on_next(None)  # gibt dem clicked-event mit, dass der Button geklickt wurde
                return True
            else:  # falls nicht geclickt wird wird getestet, ob gehovert wird
                is_hovered((mouse_x, mouse_y, mouse_state))
                return False

        def resize(data):  # passt alle Objekte an, wenn sich die Bildschirmgröße ändert
            # konvertiert die Prozentangaben zu Pixeln
            self.x_px, self.y_px, self.width_px, self.height_px = Refactor.percent_to_pixel(x, y, width, height, data)

            # skaliert das Hintergrund-Rechteck
            self.borderRectangle.x = self.x_px
            self.borderRectangle.y = self.y_px
            self.borderRectangle.width = self.width_px
            self.borderRectangle.height = self.height_px

            # skaliert das Vordergrund-Rechteck
            self.rectangle.x = self.x_px + color_scheme.border_thickness
            self.rectangle.y = self.y_px + color_scheme.border_thickness
            self.rectangle.width = self.width_px - 2 * color_scheme.border_thickness
            self.rectangle.height = self.height_px - 2 * color_scheme.border_thickness

            # skaliert den Text
            self.label.x = self.x_px+self.width_px//2
            self.label.y = self.y_px+self.height_px//2
            self.label.font_size = self.width_px//(100//font_size)

        # erstellt Subscriptions, um auf Events reagieren zu können, und fängt sie ab
        sublist.append(events.size.subscribe(resize))
        sublist.append(events.mouse.subscribe(is_hovered))
        sublist.append(events.mouse_button.subscribe(button_clicked))

        # eigenes Event des Buttons, welches abfängt, wenn der Button gedrückt wird
        self.clicked = Subject()


# nicht klickbare Variante für Überschiften o.ä.
class BorderedRectangle: # Es wird keine Klasse erweitert, damit man die Objekte in der Runtime neu zeichnen kann
    def __init__(self, text,
                 x, y, width, height,  # alle Angaben in %
                 color_scheme, font_scheme, font_size,  # für Aussehen
                 events,  # die events aus game.py werden mitgegeben, auf Veränderungen zu reagieren
                 sublist,  # Liste an Subscriptions des aktuellen Controllers
                 batch=None, group=None):  # Batch ermöglicht, dass alles gleichzeitig gerendert wird. Dadurch läuft das Programm effizienter

        # konvertiert die Prozentangaben zu Pixeln in Abhängigkeit der Fenstergröße
        x_px, y_px, width_px, height_px = Refactor.percent_to_pixel(x, y, width, height, events.size.value)

        # zeichnet ein Rechteck in den Hintergrund, welches die Border ergibt
        self.borderRectangle = pyglet.shapes.Rectangle(x_px, y_px, width_px, height_px,
                                                       color_scheme.border,  # Style wird mitgegeben
                                                       batch=batch, group=None)

        # Zeichnet das Rechteck
        self.rectangle = pyglet.shapes.Rectangle(x_px + color_scheme.border_thickness,
                                                 y_px + color_scheme.border_thickness,
                                                 width_px - 2 * color_scheme.border_thickness,
                                                 height_px - 2 * color_scheme.border_thickness,
                                                 color_scheme.color,  # Style wird mitgegeben
                                                 batch=batch, group=None)

        # Zeichnet den Text in die Mitte des Rechteckes
        self.label = pyglet.text.Label(text, x=x_px + width_px // 2, y=y_px + height_px // 2,
                                       # Text wird in die Mitte des Buttons gezeichnet
                                       anchor_x="center", anchor_y="center",
                                       # Text wird in die Mitte des Buttons gezeichnet
                                       batch=batch, font_name=font_scheme.font_name,
                                       font_size=width_px // (100 // font_size), color=color_scheme.text)

        def resize(data):  # passt alle Objekte an, wenn sich die Bildschirmgröße ändert
            # konvertiert die Prozentangaben zu Pixeln
            self.x_px, self.y_px, self.width_px, self.height_px = Refactor.percent_to_pixel(x, y, width, height, data)

            # skaliert das Hintergrund-Rechteck
            self.borderRectangle.x = self.x_px
            self.borderRectangle.y = self.y_px
            self.borderRectangle.width = self.width_px
            self.borderRectangle.height = self.height_px

            # skaliert das Vordergrund-Rechteck
            self.rectangle.x = self.x_px + color_scheme.border_thickness
            self.rectangle.y = self.y_px + color_scheme.border_thickness
            self.rectangle.width = self.width_px - 2 * color_scheme.border_thickness
            self.rectangle.height = self.height_px - 2 * color_scheme.border_thickness

            # skaliert den Text
            self.label.x = self.x_px + self.width_px // 2
            self.label.y = self.y_px + self.height_px // 2
            self.label.font_size = self.width_px // (100 // font_size)

        # erstellt Subscriptions, um auf Events reagieren zu können, und fängt sie ab
        sublist.append(events.size.subscribe(resize))


class SpriteButton(pyglet.sprite.Sprite):  # Pyglet Sprite wird erweitert um Bilder klickbar machen zu können (nicht reines Image, da man das nicht skalieren kann)
    def __init__(self, path,
                 x, y, width, height,  # alle Angaben in %
                 color_scheme,  # für Aussehen
                 events,  # die events aus game.py werden mitgegeben, auf Veränderungen zu reagieren
                 sublist,  # Liste an Subscriptions des aktuellen Controllers
                 batch=None, group=None):  # Batch ermöglicht, dass alles gleichzeitig gerendert wird. Dadurch läuft das Programm effizienter

        # konvertiert die Prozentangaben zu Pixeln
        x_px, y_px, width_px, height_px = Refactor.percent_to_pixel(x, y, width, height, events.size.value)

        # zeichnet das Bild in der richtigen Größe
        image = pyglet.image.load(path)
        pyglet.sprite.Sprite.__init__(self, image, x_px, y_px, batch=batch)
        self.scale_x = width_px / self.width  # skaliert das Bild auf die angegebene Prozentgröße des Fensters
        self.scale_y = height_px / self.height

        # speichert die Standard-Maße des Bildes ab
        normal_width = self.width
        normal_height = self.height

        def is_hovered(data):  # wird aufgerufen um den Button visuell anzupassen, falls er gehovert wird
            mouse_x, mouse_y, buttons = data  # buttons zeigt den gedrückten knopf: Links=1, Rad=2, Rechts=4
            if buttons is False and x_px <= int(mouse_x) <= x_px+width_px and y_px <= int(mouse_y) <= y_px+height_px: # testet ob Maus über dem Button ist, falls ja wird er gefärbt
                self.color = color_scheme.img_hover
                return True
            elif buttons is False:  # elif verhindert, dass gehaltene Knöpfe überschrieben werden
                self.color = (255, 255, 255)  # Bild ist standardmäßig normal
                return False

        def button_clicked(data):  # wird aufgerufen um den Button anzupassen, falls er geklickt wird
            mouse_state, mouse_x, mouse_y, buttons = data  # buttons zeigt den gedrückten knopf: Links=1, Rad=2, Rechts=4
            if mouse_state is True and buttons == 1 and x_px <= int(mouse_x) <= x_px+width_px and y_px <= int(mouse_y) <= y_px+height_px:
                self.color = color_scheme.img_click
                self.clicked.on_next(None)  # gibt dem clicked-event mit, dass der Button geklickt wurde
                return True
            else:  # falls nicht geclickt wird wird getestet, ob gehovert wird
                is_hovered((mouse_x, mouse_y, mouse_state))
                return False

        def resize(data):  # passt alle Objekte an, wenn sich die Bildschirmgröße ändert
            # konvertiert die Prozentangaben zu Pixeln
            self.x_px, self.y_px, self.width_px, self.height_px = Refactor.percent_to_pixel(x, y, width, height, data)

            # skaliert das Bild auf die angegebene Prozentgröße des Fensters
            self.scale_x = self.width_px / normal_width  # skaliert das Bild auf die angegebene Pixelzahl
            self.scale_y = self.height_px / normal_height

        # erstellt Subscriptions, um auf Events reagieren zu können, und fängt sie ab
        sublist.append(events.size.subscribe(resize))
        sublist.append(events.mouse.subscribe(is_hovered))
        sublist.append(events.mouse_button.subscribe(button_clicked))


# nicht klickbare Variante
class Sprite(pyglet.sprite.Sprite):
    def __init__(self, path,
                 x, y, width, height,  # alle Angaben in %
                 events,  # die events aus game.py werden mitgegeben, auf Veränderungen zu reagieren
                 sublist,  # Liste an Subscriptions des aktuellen Controllers
                 batch=None, group=None):  # Batch ermöglicht, dass alles gleichzeitig gerendert wird. Dadurch läuft das Programm effizienter:

        # konvertiert die Prozentangaben zu Pixeln
        x_px, y_px, width_px, height_px = Refactor.percent_to_pixel(x, y, width, height, events.size.value)

        # zeichnet das Bild in der richtigen Größe
        image = pyglet.image.load(path)
        pyglet.sprite.Sprite.__init__(self, image, x_px, y_px, batch=batch)

        # speichert die Standard-Maße des Bildes ab
        normal_width = self.width
        normal_height = self.height

        # skaliert das Bild auf die angegebene Prozentgröße des Fensters
        self.scale_x = width_px / normal_width
        self.scale_y = height_px / normal_height

        def resize(data):  # passt alle Objekte an, wenn sich die Bildschirmgröße ändert
            # konvertiert die Prozentangaben zu Pixeln
            self.x_px, self.y_px, self.width_px, self.height_px = Refactor.percent_to_pixel(x, y, width, height, data)

            # skaliert das Bild auf die angegebene Prozentgröße des Fensters
            self.scale_x = self.width_px / normal_width  # skaliert das Bild auf die angegebene Pixelzahl
            self.scale_y = self.height_px / normal_height

        # erstellt Subscriptions, um auf Events reagieren zu können, und fängt sie ab
        sublist.append(events.size.subscribe(resize))


# Pyglet Sprite wird erweitert um Bilder klickbar machen zu können (nicht reines Image, da man das nicht skalieren kann)
class BorderedSpriteButton(pyglet.sprite.Sprite):
    def __init__(self, path,
                 x, y, width, height,  # alle Angaben in %
                 color_scheme,  # für Aussehen
                 events,  # die events aus game.py werden mitgegeben, auf Veränderungen zu reagieren
                 sublist,  # Liste an Subscriptions des aktuellen Controllers
                 batch=None, group=None):  # Batch ermöglicht, dass alles gleichzeitig gerendert wird. Dadurch läuft das Programm effizienter

        # konvertiert die Prozentangaben zu Pixeln
        x_px, y_px, width_px, height_px = Refactor.percent_to_pixel(x, y, width, height, events.size.value)

        # zeichnet ein Rechteck in den Hintergrund, welches die Border ergibt
        self.borderRectangle = pyglet.shapes.Rectangle(x_px, y_px, width_px, height_px,
                                                       color_scheme.border,  # Style wird mitgegeben
                                                       batch=batch, group=None)

        # zeichnet das Bild in der richtigen Größe
        image = pyglet.image.load(path)
        pyglet.sprite.Sprite.__init__(self, image,
                                      x_px + color_scheme.border_thickness,
                                      y_px + color_scheme.border_thickness, batch=batch)

        # speichert die Standard-Maße des Bildes ab
        normal_width = self.width
        normal_height = self.height

        # skaliert das Bild auf die angegebene Prozentgröße des Fensters abzüglich der Border
        self.scale_x = (width_px - 2 * color_scheme.border_thickness) / self.width  # skaliert das Bild auf die angegebene Pixelzahl
        self.scale_y = (height_px - 2 * color_scheme.border_thickness) / self.height

        def is_hovered(data):  # wird aufgerufen um den Button visuell anzupassen, falls er gehovert wird
            mouse_x, mouse_y, buttons = data  # buttons zeigt den gedrückten knopf: Links=1, Rad=2, Rechts=4
            if buttons is False and x_px <= int(mouse_x) <= x_px+width_px and y_px <= int(mouse_y) <= y_px+height_px: # testet ob Maus über dem Button ist, falls ja wird er gefärbt
                self.color = color_scheme.img_hover
                self.borderRectangle.color = color_scheme.hover_border
                return True
            elif buttons is False:  # elif verhindert, dass gehaltene Knöpfe überschrieben werden
                self.color = (255, 255, 255)  # Bild ist standardmäßig normal
                self.borderRectangle.color = color_scheme.border
                return False

        def button_clicked(data):  # wird aufgerufen um den Button anzupassen, falls er geklickt wird
            mouse_state, mouse_x, mouse_y, buttons = data  # buttons zeigt den gedrückten knopf: Links=1, Rad=2, Rechts=4
            if mouse_state is True and buttons == 1 and x_px <= int(mouse_x) <= x_px+width_px and y_px <= int(mouse_y) <= y_px+height_px:
                self.color = color_scheme.img_click
                self.borderRectangle.color = color_scheme.click_border
                self.clicked.on_next(None)  # gibt dem clicked-event mit, dass der Button geklickt wurde
                return True
            else:  # falls nicht geclickt wird wird getestet ob gehovert wird
                is_hovered((mouse_x, mouse_y, mouse_state))
                return False

        def resize(data):  # passt alle Objekte an, wenn sich die Bildschirmgröße ändert
            # konvertiert die Prozentangaben zu Pixeln
            self.x_px, self.y_px, self.width_px, self.height_px = Refactor.percent_to_pixel(x, y, width, height, data)

            # skaliert das Bild auf die angegebene Prozentgröße des Fensters abzüglich der Border
            self.scale_x = (self.width_px - 2 * color_scheme.border_thickness) / normal_width  # skaliert das Bild auf die angegebene Pixelzahl
            self.scale_y = (self.height_px - 2 * color_scheme.border_thickness) / normal_height

            # skaliert die Border auf die angegebene Prozentgröße des Fensters
            self.borderRectangle.width = self.width_px
            self.borderRectangle.height = self.height_px

        # erstellt Subscriptions, um auf Events reagieren zu können, und fängt sie ab
        sublist.append(events.size.subscribe(resize))
        sublist.append(events.mouse.subscribe(is_hovered))
        sublist.append(events.mouse_button.subscribe(button_clicked))

        # eigenes Event des Buttons, welches abfängt, wenn der Button gedrückt wird
        self.clicked = Subject()


# Pyglet Sprite wird erweitert (nicht reines Image, da man das nicht skalieren kann)
class BorderedSprite(pyglet.sprite.Sprite):
    def __init__(self, path,
                 x, y, width, height,  # alle Angaben in %
                 color_scheme,  # für Aussehen
                 events,  # die events aus game.py werden mitgegeben, auf Veränderungen zu reagieren
                 sublist,  # Liste an Subscriptions des aktuellen Controllers
                 batch=None, group=None):  # Batch ermöglicht, dass alles gleichzeitig gerendert wird. Dadurch läuft das Programm effizienter

        # konvertiert die Prozentangaben zu Pixeln
        x_px, y_px, width_px, height_px = Refactor.percent_to_pixel(x, y, width, height, events.size.value)

        # zeichnet ein Rechteck in den Hintergrund, welches die Border ergibt
        self.borderRectangle = pyglet.shapes.Rectangle(x_px, y_px, width_px, height_px,
                                                       color_scheme.border,  # Style wird mitgegeben
                                                       batch=batch, group=None)

        # zeichnet das Bild in der richtigen Größe
        image = pyglet.image.load(path)
        pyglet.sprite.Sprite.__init__(self, image,
                                      x_px + color_scheme.border_thickness,
                                      y_px + color_scheme.border_thickness, batch=batch)

        # speichert die Standard-Maße des Bildes ab
        normal_width = self.width
        normal_height = self.height

        # skaliert das Bild auf die angegebene Prozentgröße des Fensters abzüglich der Border
        self.scale_x = (width_px - 2 * color_scheme.border_thickness) / self.width  # skaliert das Bild auf die angegebene Pixelzahl
        self.scale_y = (height_px - 2 * color_scheme.border_thickness) / self.height

        def resize(data):  # passt alle Objekte an, wenn sich die Bildschirmgröße ändert
            # konvertiert die Prozentangaben zu Pixeln
            self.x_px, self.y_px, self.width_px, self.height_px = Refactor.percent_to_pixel(x, y, width, height, data)

            # skaliert das Bild auf die angegebene Prozentgröße des Fensters abzüglich der Border
            self.scale_x = (self.width_px - 2 * color_scheme.border_thickness) / normal_width
            self.scale_y = (self.height_px - 2 * color_scheme.border_thickness) / normal_height

            # skaliert die Border auf die angegebene Prozentgröße des Fensters
            self.borderRectangle.width = self.width_px
            self.borderRectangle.height = self.height_px

        # erstellt Subscriptions, um auf Events reagieren zu können, und fängt sie ab
        sublist.append(events.size.subscribe(resize))


# Pyglet Sprite wird erweitert um variabel Gifs anzuzeigen (nicht reines Image, da man das nicht skalieren kann)
class Gif(pyglet.sprite.Sprite):  # lädt ein Gif
    def __init__(self, path,
                 x, y, width, height,  # alle Angaben in %
                 duration, loop,  # duration = Zeit für einen Durchlauf des Gif
                 events,  # die events aus game.py werden mitgegeben, auf Veränderungen zu reagieren
                 sublist,  # Liste an Subscriptions des aktuellen Controllers
                 batch=None, group=None):  # Batch ermöglicht, dass alles gleichzeitig gerendert wird. Dadurch läuft das Programm effizienter

        # konvertiert die Prozentangaben zu Pixeln
        x_px, y_px, width_px, height_px = Refactor.percent_to_pixel(x, y, width, height, events.size.value)

        # erstellt eine Liste der einzelnen Bilder des Gifs
        image = pyglet.image.load_animation(path)
        animation_frames = []
        for frames in image.frames:
            animation_frames.append(frames.__getattribute__("image"))

        # erstellt aus den einzelnen Bildern eine Animation der gewünschten Länge. Loop erlaubt ununterbrochene Wiederholung der Animation
        animation = image.from_image_sequence(animation_frames, duration=duration / len(animation_frames), loop=loop)
        pyglet.sprite.Sprite.__init__(self, animation, x_px, y_px, batch=batch)

        # speichert die Standard-Maße des Gifs
        normal_width = self.width
        normal_height = self.height

        # skaliert das Bild auf die angegebene Prozentgröße des Fensters
        self.scale_x = width_px / normal_width
        self.scale_y = height_px / normal_height

        def resize(data):  # passt alle Objekte an, wenn sich die Bildschirmgröße ändert
            # konvertiert die Prozentangaben zu Pixeln
            self.x_px, self.y_px, self.width_px, self.height_px = Refactor.percent_to_pixel(x, y, width, height, data)

            # skaliert das Bild auf die angegebene Prozentgröße des Fensters
            self.scale_x = self.width_px / normal_width
            self.scale_y = self.height_px / normal_height

        # erstellt Subscriptions, um auf Events reagieren zu können, und fängt sie ab
        sublist.append(events.size.subscribe(resize))


# Pyglet Sprite wird erweitert um variabel Gifs anzuzeigen und klickbar zu machen (nicht reines Image, da man das nicht skalieren kann)
class GifButton(pyglet.sprite.Sprite):  # lädt ein Gif
    def __init__(self, path,
                 x, y, width, height,  # alle Angaben in %
                 duration, loop,  # duration = Zeit für einen Durchlauf des Gif
                 events,  # die events aus game.py werden mitgegeben, auf Veränderungen zu reagieren
                 sublist,  # Liste an Subscriptions des aktuellen Controllers
                 batch=None, group=None):  # Batch ermöglicht, dass alles gleichzeitig gerendert wird. Dadurch läuft das Programm effizienter

        # konvertiert die Prozentangaben zu Pixeln
        x_px, y_px, width_px, height_px = Refactor.percent_to_pixel(x, y, width, height, events.size.value)

        # erstellt eine Liste der einzelnen Bilder des Gifs
        image = pyglet.image.load_animation(path)
        animation_frames = []
        for frames in image.frames:
            animation_frames.append(frames.__getattribute__("image"))

        # erstellt aus den einzelnen Bildern eine Animation der gewünschten Länge. Loop erlaubt ununterbrochene Wiederholung der Animation
        animation = image.from_image_sequence(animation_frames, duration=duration / len(animation_frames), loop=loop)
        pyglet.sprite.Sprite.__init__(self, animation, x_px, y_px, batch=batch)

        # speichert die Standard-Maße des Gifs
        normal_width = self.width
        normal_height = self.height

        # skaliert das Bild auf die angegebene Prozentgröße des Fensters
        self.scale_x = width_px / normal_width
        self.scale_y = height_px / normal_height

        def button_clicked(data):  # wird aufgerufen um den Button anzupassen, falls er geklickt wird
            mouse_state, mouse_x, mouse_y, buttons = data  # buttons zeigt den gedrückten knopf: Links=1, Rad=2, Rechts=4
            if mouse_state is True and buttons == 1 and self.x_px <= int(mouse_x) <= self.x_px+self.width_px and self.y_px <= int(mouse_y) <= self.y_px+self.height_px:
                self.clicked.on_next(None)  # gibt dem clicked-event mit, dass der Button geklickt wurde
                return True
            else:  # falls nicht geklickt
                return False

        def resize(data):  # passt alle Objekte an, wenn sich die Bildschirmgröße ändert
            # konvertiert die Prozentangaben zu Pixeln
            self.x_px, self.y_px, self.width_px, self.height_px = Refactor.percent_to_pixel(x, y, width, height, data)

            # skaliert das Bild auf die angegebene Prozentgröße des Fensters
            self.scale_x = self.width_px / normal_width  # skaliert das Bild auf die angegebene Pixelzahl
            self.scale_y = self.height_px / normal_height

        # erstellt Subscriptions, um auf Events reagieren zu können, und fängt sie ab
        sublist.append(events.size.subscribe(resize))
        sublist.append(events.mouse_button.subscribe(button_clicked))

        # eigenes Event des Buttons, welches abfängt, wenn der Button gedrückt wird
        self.clicked = Subject()


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
