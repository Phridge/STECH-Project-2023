import math
from collections import namedtuple

import reactivex
from reactivex.disposable import CompositeDisposable
from reactivex.subject import Subject
import pyglet
from pyglet.gui.widgets import Slider
from pyglet.text import Label, HTMLLabel, DocumentLabel
from events import Event, Var, Disposable

# Erweitert die Pyglet-Klassen, um daraus Buttons, Banner und Formen zu machen


class UIElement(Disposable):

    def percent_to_pixel(self, x, y, width, height, window_data):
        """
        Ermöglicht die Umrechnung von Prozentangaben in Pixel, damit die ui-elements die Werte nutzen können
        :param x: X-Koordinate in %
        :param y: Y-Koordinate in %
        :param width: Breite des Elements in %
        :param height: Höhe des Elements in %
        :param window_data: Event-Daten, die die aktuelle Höhe und Breite des Fensters beinhalten
        :return: X, Y, Breite und Höhe in Pixeln
        """
        screen_width, screen_height = window_data
        x_px = x * screen_width // 100
        y_px = y * screen_height // 100
        width_px = width * screen_width // 100
        height_px = height * screen_height // 100
        return x_px, y_px, width_px, height_px

    def resize(self, x, y, width, height, window_size, color_scheme=None, font_size=None):
        """
        Wird aufgerufen, wenn sich die Größe des Fensters verändert. Skaliert alle Elemente auf ihre relativen Größen

        :param x: gewünschte x-Koordinate des linken Element-Randes in %
        :param y: gewünschte y-Koordinate des unteren Element-Randes in %
        :param width: gewünschte Breite des Elements in %
        :param height: gewünschte Höhe des Elements in %
        :param window_size: aktuelle Größe des Fensters
        :param color_scheme: aktuelles Farbschema
        :param font_size: Schriftgröße des Elements
        """
        # konvertiert die Prozentangaben zu Pixeln
        self.x_px, self.y_px, self.width_px, self.height_px = self.percent_to_pixel(x, y, width, height, window_size)

        border = 0

        # skaliert das Hintergrund-Rechteck, falls es eins gibt
        if 'borderRectangle' in vars(self):
            self.borderRectangle.x = self.x_px
            self.borderRectangle.y = self.y_px
            self.borderRectangle.width = self.width_px
            self.borderRectangle.height = self.height_px
            border = color_scheme.border_thickness

        # skaliert das Vordergrund-Rechteck, falls es eins gibt
        if 'rectangle' in vars(self):
            self.rectangle.x = self.x_px + border
            self.rectangle.y = self.y_px + border
            self.rectangle.width = self.width_px - 2 * border
            self.rectangle.height = self.height_px - 2 * border

        # skaliert den Text, falls es ihn gibt
        if 'label' in vars(self):
            self.label.x = self.x_px + self.width_px // 2
            self.label.y = self.y_px + self.height_px // 2
            self.label.font_size = self.width_px // (100 / font_size)

        # skaliert Bilder und Gifs, falls es welche gibt
        if isinstance(self, (Sprite, BorderedSprite, BorderedSpriteButton, GifButton, Gif)):
            self.scale_x = (self.width_px - 2 * border) / self.normal_width  # skaliert das Bild auf die angegebene Pixelzahl
            self.scale_y = (self.height_px - 2 * border) / self.normal_height


class BorderedRectangle(UIElement):
    def __init__(self, text, x, y, width, height, color_scheme, font_scheme, font_size, events, batch=None, group=pyglet.graphics.Group(order=0)):
        """
        Rechtecktiges Element mit einer Border. Nicht klickbar. Nutzung für einfache Überschriften oder Textkästen.
        Es wird keine Klasse erweitert, damit man die Objekte in der Runtime neu zeichnen kann.

        :param text:
        :param x: X-Koordinate in %
        :param y: Y-Koordinate in %
        :param width: Breite des Elements in %
        :param height: Höhe des Elements in %
        :param color_scheme: Style-Klasse der Datei color_scheme.py
        :param font_scheme: Schrift-Klasse der Datei color_scheme.py
        :param font_size: Schrift-Größe
        :param events: events des games
        :param batch: aktueller Pyglet-Batch --> steigert Zeichen-Effizienz
        """

        # konvertiert die Prozentangaben zu Pixeln in Abhängigkeit der Fenstergröße
        x_px, y_px, width_px, height_px = self.percent_to_pixel(x, y, width, height, events.size.value)

        # zeichnet ein Rechteck in den Hintergrund, welches die Border ergibt
        self.borderRectangle = pyglet.shapes.Rectangle(x_px, y_px, width_px, height_px,
                                                       color_scheme.border,  # Style wird mitgegeben
                                                       batch=batch, group=group)

        # Zeichnet das Rechteck
        self.rectangle = pyglet.shapes.Rectangle(x_px + color_scheme.border_thickness,
                                                 y_px + color_scheme.border_thickness,
                                                 width_px - 2 * color_scheme.border_thickness,
                                                 height_px - 2 * color_scheme.border_thickness,
                                                 color_scheme.color,  # Style wird mitgegeben
                                                 batch=batch, group=group)

        # Zeichnet den Text in die Mitte des Rechteckes
        self.label = pyglet.text.Label(text, x=x_px + width_px // 2, y=y_px + height_px // 2,
                                       # Text wird in die Mitte des Buttons gezeichnet
                                       anchor_x="center", anchor_y="center",
                                       # Text wird in die Mitte des Buttons gezeichnet
                                       batch=batch, font_name=font_scheme.font_name,
                                       font_size=width_px // (100 / font_size), color=color_scheme.text, group=group)

        # erstellt Subscriptions, um auf Events reagieren zu können, und fängt sie ab
        self._sub = events.size.subscribe(lambda _: self.resize(x, y, width, height, events.size.value, color_scheme, font_size))


class BorderedRectangleButton(UIElement):
    def __init__(self, text, x, y, width, height, color_scheme, font_scheme, font_size, events, batch=None, group=pyglet.graphics.Group(order=0)):
        """
        Rechtecktiger Button mit einer Border. Er kann gehovert und geclickt werden.
        Es wird keine Klasse erweitert, damit man die Objekte in der Runtime neu zeichnen kann.

        :param text:
        :param x: X-Koordinate in %
        :param y: Y-Koordinate in %
        :param width: Breite des Elements in %
        :param height: Höhe des Elements in %
        :param color_scheme: Style-Klasse der Datei color_scheme.py
        :param font_scheme: Schrift-Klasse der Datei color_scheme.py
        :param font_size: Schrift-Größe
        :param events: events des games
        :param batch: aktueller Pyglet-Batch --> steigert Zeichen-Effizienz
        """

        # konvertiert die Prozentangaben zu Pixeln in Abhängigkeit der Fenstergröße
        x_px, y_px, width_px, height_px = self.percent_to_pixel(x, y, width, height, events.size.value)

        # zeichnet ein Rechteck in den Hintergrund, welches die Border ergibt
        self.borderRectangle = pyglet.shapes.Rectangle(x_px, y_px, width_px, height_px,
                                                       color_scheme.border,  # Style wird mitgegeben
                                                       batch=batch, group=group)

        # Zeichnet das Rechteck
        self.rectangle = pyglet.shapes.Rectangle(x_px + color_scheme.border_thickness,
                                                 y_px + color_scheme.border_thickness,
                                                 width_px - 2 * color_scheme.border_thickness,
                                                 height_px - 2 * color_scheme.border_thickness,
                                                 color_scheme.color,  # Style wird mitgegeben
                                                 batch=batch, group=group)

        # Zeichnet den Text in die Mitte des Rechteckes
        self.label = pyglet.text.Label(text, x=x_px + width_px // 2, y=y_px + height_px // 2,
                                       # Text wird in die Mitte des Buttons gezeichnet
                                       anchor_x="center", anchor_y="center",
                                       # Text wird in die Mitte des Buttons gezeichnet
                                       batch=batch, font_name=font_scheme.font_name,
                                       font_size=width_px // (100 / font_size), color=color_scheme.text, group=group)

        def is_hovered(data):
            """
            Wird aufgerufen, wenn die Maus sich bewegt. Testet, ob sie über dem Button ist und reagiert entsprechend.

            :param data: Aktuelle Position der Maus (x, y)
            """
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

        def button_clicked(data):
            """
            Wird aufgerufen, wenn ein Maus-Button gedrückt wird. Testet, ob sie über dem Button ist und reagiert entsprechend.

            :param data: Aktueller Zustand und aktuelle Position der Maus (bool, x, y, buttons)
            """
            mouse_state, mouse_x, mouse_y, buttons = data  # buttons zeigt den gedrückten knopf: Links=1, Rad=2, Rechts=4
            if mouse_state is True and buttons == 1 and self.x_px <= int(mouse_x) <= self.x_px+self.width_px and self.y_px <= int(mouse_y) <= self.y_px+self.height_px:
                self.rectangle.color = color_scheme.click
                self.borderRectangle.color = color_scheme.click_border
                self.label.color = color_scheme.click_text
                self.clicked.on_next(True)  # gibt dem clicked-event mit, dass der Button geklickt wurde
                return True
            else:  # falls nicht geclickt wird wird getestet, ob gehovert wird
                is_hovered((mouse_x, mouse_y, mouse_state))
                return False

        # erstellt Subscriptions, um auf Events reagieren zu können, und fängt sie ab
        self._subs = CompositeDisposable([
            events.size.subscribe(lambda _: self.resize(x, y, width, height, events.size.value, color_scheme, font_size)),
            events.mouse.subscribe(is_hovered),
            events.mouse_button.subscribe(button_clicked)
        ])

        # eigenes Event des Buttons, welches abfängt, wenn der Button gedrückt wird
        self.clicked = Subject()


class InputBox(UIElement):
    def __init__(self, text, x, y, width, height, color_scheme, font_scheme, font_size, events,
                 batch=None, group=pyglet.graphics.Group(order=0)):
        """
        Rechtecktiges Element mit einer Border. Nicht klickbar. Nutzung für einfache Überschriften oder Textkästen.
        Der im Button angezeigte Text kann vollständig eingegeben werden, um ihn zu aktivieren.
        Es wird keine Klasse erweitert, damit man die Objekte in der Runtime neu zeichnen kann.

        :param text:
        :param x: X-Koordinate in %
        :param y: Y-Koordinate in %
        :param width: Breite des Elements in %
        :param height: Höhe des Elements in %
        :param color_scheme: Style-Klasse der Datei color_scheme.py
        :param font_scheme: Schrift-Klasse der Datei color_scheme.py
        :param font_size: Schrift-Größe
        :param events: events des games
        :param batch: aktueller Pyglet-Batch --> steigert Zeichen-Effizienz
        """

        # konvertiert die Prozentangaben zu Pixeln in Abhängigkeit der Fenstergröße
        x_px, y_px, width_px, height_px = self.percent_to_pixel(x, y, width, height, events.size.value)

        # zeichnet ein Rechteck in den Hintergrund, welches die Border ergibt
        self.borderRectangle = pyglet.shapes.Rectangle(x_px, y_px, width_px, height_px,
                                                       color_scheme.border,  # Style wird mitgegeben
                                                       batch=batch, group=group)

        # Zeichnet das Rechteck
        self.rectangle = pyglet.shapes.Rectangle(x_px + color_scheme.border_thickness,
                                                 y_px + color_scheme.border_thickness,
                                                 width_px - 2 * color_scheme.border_thickness,
                                                 height_px - 2 * color_scheme.border_thickness,
                                                 color_scheme.color,  # Style wird mitgegeben
                                                 batch=batch, group=group)


        # Zeichnet den Text in die Mitte des Rechteckes
        self.label = pyglet.text.Label(text, x=x_px + width_px // 2, y=y_px + height_px // 2,
                                       # Text wird in die Mitte des Buttons gezeichnet
                                       anchor_x="center", anchor_y="center",
                                       # Text wird in die Mitte des Buttons gezeichnet
                                       batch=batch, font_name=font_scheme.font_name,
                                       font_size=width_px // (100 / font_size), color=color_scheme.text, group=group)

        def update_text(data):
            if self.label.text and data == self.label.text[0]: self.label.text = self.label.text[1:]
            if not self.label.text:
                self.clicked.on_next(True)  # gibt dem clicked-event mit, dass der Button geklickt wurde

        # erstellt Subscriptions, um auf Events reagieren zu können, und fängt sie ab
        self._subs = CompositeDisposable([
            events.size.subscribe(lambda _: self.resize(x, y, width, height, events.size.value, color_scheme, font_size)),
            events.text.subscribe(update_text)
        ])

        # eigenes Event des Buttons, welches abfängt, wenn der Button gedrückt wird
        self.clicked = Subject()


class InputButton(UIElement):
    def __init__(self, text, x, y, width, height, color_scheme, font_scheme, font_size, events, batch=None, group=pyglet.graphics.Group(order=0)):
        """
        Rechtecktiger Button mit einer Border. Er kann gehovert und geclickt werden.
        Zudem kann der im Button angezeigte Text vollständig eingegeben werden, um ihn ebenfalls zu aktivieren.
        Es wird keine Klasse erweitert, damit man die Objekte in der Runtime neu zeichnen kann.

        :param text:
        :param x: X-Koordinate in %
        :param y: Y-Koordinate in %
        :param width: Breite des Elements in %
        :param height: Höhe des Elements in %
        :param color_scheme: Style-Klasse der Datei color_scheme.py
        :param font_scheme: Schrift-Klasse der Datei color_scheme.py
        :param font_size: Schrift-Größe
        :param events: events des games
        :param batch: aktueller Pyglet-Batch --> steigert Zeichen-Effizienz
        """

        self.color_scheme = color_scheme
        self.font_size = font_size

        # konvertiert die Prozentangaben zu Pixeln in Abhängigkeit der Fenstergröße
        x_px, y_px, width_px, height_px = self.percent_to_pixel(x, y, width, height, events.size.value)

        # zeichnet ein Rechteck in den Hintergrund, welches die Border ergibt
        self.borderRectangle = pyglet.shapes.Rectangle(x_px, y_px, width_px, height_px,
                                                       color_scheme.border,  # Style wird mitgegeben
                                                       batch=batch, group=group)

        # Zeichnet das Rechteck
        self.rectangle = pyglet.shapes.Rectangle(x_px + color_scheme.border_thickness,
                                                 y_px + color_scheme.border_thickness,
                                                 width_px - 2 * color_scheme.border_thickness,
                                                 height_px - 2 * color_scheme.border_thickness,
                                                 color_scheme.color,  # Style wird mitgegeben
                                                 batch=batch, group=group)

        self.pulse = 0

        # Zeichnet den Text in die Mitte des Rechteckes
        self.label = pyglet.text.Label(text, x=x_px + width_px // 2, y=y_px + height_px // 2,
                                       # Text wird in die Mitte des Buttons gezeichnet
                                       anchor_x="center", anchor_y="center",
                                       # Text wird in die Mitte des Buttons gezeichnet
                                       batch=batch, font_name=font_scheme.font_name,
                                       font_size=(width_px // (100 / font_size))+ self.pulse, color=color_scheme.text, group=group)

        pyglet.clock.schedule_interval_soft(self.pulse_label, 0.05)

        def is_hovered(data):
            """
            Wird aufgerufen, wenn die Maus sich bewegt. Testet, ob sie über dem Button ist und reagiert entsprechend.

            :param data: Aktuelle Position der Maus (x, y)
            """
            mouse_x, mouse_y, buttons = data  # buttons zeigt den gedrückten knopf: Links=1, Rad=2, Rechts=4
            if buttons is False and self.x_px <= int(mouse_x) <= self.x_px + self.width_px and self.y_px <= int(
                    mouse_y) <= self.y_px + self.height_px:  # testet ob Maus über dem Button ist, falls ja wird er gefärbt
                self.rectangle.color = color_scheme.hover
                self.borderRectangle.color = color_scheme.hover_border
                self.label.color = color_scheme.hover_text
                return True
            elif buttons is False:  # elif verhindert, dass gehaltene Knöpfe überschrieben werden
                self.rectangle.color = color_scheme.color
                self.borderRectangle.color = color_scheme.border
                return False

        def button_clicked(data):
            """
            Wird aufgerufen, wenn ein Maus-Button gedrückt wird. Testet, ob sie über dem Button ist und reagiert entsprechend.

            :param data: Aktueller Zustand und aktuelle Position der Maus (bool, x, y, buttons)
            """
            mouse_state, mouse_x, mouse_y, buttons = data  # buttons zeigt den gedrückten knopf: Links=1, Rad=2, Rechts=4
            if mouse_state is True and buttons == 1 and self.x_px <= int(
                    mouse_x) <= self.x_px + self.width_px and self.y_px <= int(mouse_y) <= self.y_px + self.height_px:
                self.rectangle.color = color_scheme.click
                self.borderRectangle.color = color_scheme.click_border
                self.label.color = color_scheme.click_text
                self.clicked.on_next(True)  # gibt dem clicked-event mit, dass der Button geklickt wurde
                return True
            else:  # falls nicht geclickt wird wird getestet, ob gehovert wird
                is_hovered((mouse_x, mouse_y, mouse_state))
                return False

        def update_text(data):
            if self.label.text and data == self.label.text[0]: self.label.text = self.label.text[1:]
            if not self.label.text:
                self.clicked.on_next(True)  # gibt dem clicked-event mit, dass der Button geklickt wurde

        # erstellt Subscriptions, um auf Events reagieren zu können, und fängt sie ab
        self._subs = CompositeDisposable([
            events.size.subscribe(lambda _: self.resize(x, y, width, height, events.size.value, color_scheme, font_size)),
            events.mouse.subscribe(is_hovered),
            events.mouse_button.subscribe(button_clicked),
            events.text.subscribe(update_text),
        ])

        # eigenes Event des Buttons, welches abfängt, wenn der Button gedrückt wird
        self.clicked = Subject()

    def pulse_label(self, data):
        self.pulse += 0.05
        if self.pulse >= 4: self.pulse = 0
        if math.sin(self.pulse*math.pi) > 0 and self.pulse <= 2: text_increase = math.sin(self.pulse*math.pi)/3
        else: text_increase = 0
        self.label.color = (int(self.color_scheme.text[0]*(1-text_increase)), int(self.color_scheme.text[1]*(1-text_increase)), int(self.color_scheme.text[2]*(1-text_increase)), 255)


class SettingTextField(UIElement):
    def __init__(self, text, number_of_chars, limit, x, y, width, height, color_scheme, font_scheme, font_size, events, name,
                 batch=None, group=pyglet.graphics.Group(order=0)):
        """
        Rechtecktiges Element mit einer Border. Nicht klickbar. Zahl von 0 bis limit kann eingegeben werden.
        Es wird keine Klasse erweitert, damit man die Objekte in der Runtime neu zeichnen kann.

        :param number_of_chars: erlaubte Maximalanzahl an Zeichen
        :param limit: höchster erlaubter Eingabewert
        :param x: X-Koordinate in %
        :param y: Y-Koordinate in %
        :param width: Breite des Elements in %
        :param height: Höhe des Elements in %
        :param color_scheme: Style-Klasse der Datei color_scheme.py
        :param font_scheme: Schrift-Klasse der Datei color_scheme.py
        :param font_size: Schrift-Größe
        :param events: events des games
        :param name: Name of the element, needed to identify it inside class
        :param batch: aktueller Pyglet-Batch --> steigert Zeichen-Effizienz
        """

        self.color_scheme = color_scheme

        # konvertiert die Prozentangaben zu Pixeln in Abhängigkeit der Fenstergröße
        x_px, y_px, width_px, height_px = self.percent_to_pixel(x, y, width, height, events.size.value)
        self.active = False

        # zeichnet ein Rechteck in den Hintergrund, welches die Border ergibt
        self.borderRectangle = pyglet.shapes.Rectangle(x_px, y_px, width_px, height_px,
                                                       color_scheme.border,  # Style wird mitgegeben
                                                       batch=batch, group=group)

        # Zeichnet das Rechteck
        self.rectangle = pyglet.shapes.Rectangle(x_px + color_scheme.border_thickness,
                                                 y_px + color_scheme.border_thickness,
                                                 width_px - 2 * color_scheme.border_thickness,
                                                 height_px - 2 * color_scheme.border_thickness,
                                                 color_scheme.color,  # Style wird mitgegeben
                                                 batch=batch, group=group)

        # Zeichnet den Text in die Mitte des Rechteckes
        self.text = text
        self.label = pyglet.text.Label(self.text, x=x_px + width_px // 2, y=y_px + height_px // 2,
                                       # Text wird in die Mitte des Buttons gezeichnet
                                       anchor_x="center", anchor_y="center",
                                       # Text wird in die Mitte des Buttons gezeichnet
                                       batch=batch, font_name=font_scheme.font_name,
                                       font_size=width_px // (100 / font_size), color=color_scheme.text, group=group)

        def is_hovered(data):
            """
            Wird aufgerufen, wenn die Maus sich bewegt. Testet, ob sie über dem Button ist und reagiert entsprechend.

            :param data: Aktuelle Position der Maus (x, y)
            """
            mouse_x, mouse_y, buttons = data  # buttons zeigt den gedrückten knopf: Links=1, Rad=2, Rechts=4
            if self.active is False and buttons is False and self.x_px <= int(mouse_x) <= self.x_px + self.width_px and self.y_px <= int(
                    mouse_y) <= self.y_px + self.height_px:  # testet ob Maus über dem Button ist, falls ja wird er gefärbt
                self.rectangle.color = color_scheme.hover
                self.borderRectangle.color = color_scheme.hover_border
                self.label.color = color_scheme.hover_text
                return True
            elif self.active is False and buttons is False:  # elif verhindert, dass gehaltene Knöpfe überschrieben werden
                self.rectangle.color = color_scheme.color
                self.borderRectangle.color = color_scheme.border
                self.label.color = color_scheme.text
                return False

        def button_clicked(data):
            """
            Wird aufgerufen, wenn ein Maus-Button gedrückt wird. Testet, ob sie über dem Button ist und reagiert entsprechend.

            :param data: Aktueller Zustand und aktuelle Position der Maus (bool, x, y, buttons)
            """
            mouse_state, mouse_x, mouse_y, buttons = data  # buttons zeigt den gedrückten knopf: Links=1, Rad=2, Rechts=4
            if self.active is False and mouse_state is True and buttons == 1 and self.x_px <= int(
                    mouse_x) <= self.x_px + self.width_px and self.y_px <= int(mouse_y) <= self.y_px + self.height_px:
                self.rectangle.color = color_scheme.click
                self.borderRectangle.color = color_scheme.click_border
                self.label.color = color_scheme.click_text
                self.text = self.label.text = ""
                self.clicked.on_next(True)  # gibt dem clicked-event mit, dass der Button geklickt wurde
                return True
            elif self.active is False:  # falls nicht geclickt wird wird getestet, ob gehovert wird
                is_hovered((mouse_x, mouse_y, mouse_state))
                return False

        def update_text(data):
            if self.active and str(data).isnumeric():
                data = str(data)
                if len(self.text) < number_of_chars: self.text = self.text + data
                else: self.text = data
                if int(self.text) > limit: self.text = str(limit)
                elif int(self.text) < 0: self.text = "0"
                self.label.text = str(self.text)
                self.changed.on_next((name, str(self.text)))  # gibt dem clicked-event mit, dass der Button geklickt wurde

        # erstellt Subscriptions, um auf Events reagieren zu können, und fängt sie ab
        self._subs = CompositeDisposable([
            events.size.subscribe(lambda _: self.resize(x, y, width, height, events.size.value, color_scheme, font_size)),
            events.mouse.subscribe(is_hovered),
            events.mouse_button.subscribe(button_clicked),
            events.text.subscribe(update_text),
        ])

        # eigenes Event des Buttons, welches abfängt, wenn der Button gedrückt wird
        self.clicked = Subject()
        self.changed = Subject()

    def set_active(self, param):
        self.active = param
        if self.active:
            self.rectangle.color = self.color_scheme.click
            self.borderRectangle.color = self.color_scheme.click_border
            self.label.color = self.color_scheme.click_text
        else:
            self.rectangle.color = self.color_scheme.color
            self.borderRectangle.color = self.color_scheme.border
            self.label.color = self.color_scheme.text


class SpriteButton(pyglet.sprite.Sprite, UIElement):
    def __init__(self, path, x, y, width, height, color_scheme, events, batch=None, group=pyglet.graphics.Group(order=0)):
        """
        Rechteckiger Button mit einem Bild als Fläche. Er kann gehovert und geclickt werden.
        pyglet.sprite.Sprite wird erweitert, da es Skalierungs-Methoden hat.

        :param path: Pfad des zu zeichnenden Bildes. Vorzugsweise eine relative Pfadangabe
        :param x: X-Koordinate in %
        :param y: Y-Koordinate in %
        :param width: Breite des Elements in %
        :param height: Höhe des Elements in %
        :param color_scheme: Style-Klasse der Datei color_scheme.py
        :param events: events des games
        :param batch: aktueller Pyglet-Batch --> steigert Zeichen-Effizienz
        """

        # konvertiert die Prozentangaben zu Pixeln
        x_px, y_px, width_px, height_px = self.percent_to_pixel(x, y, width, height, events.size.value)

        # zeichnet das Bild in der richtigen Größe
        image = pyglet.image.load(path)
        pyglet.sprite.Sprite.__init__(self, image, x_px, y_px, batch=batch, group=group)
        self.scale_x = width_px / self.width  # skaliert das Bild auf die angegebene Prozentgröße des Fensters
        self.scale_y = height_px / self.height

        # speichert die Standard-Maße des Bildes ab
        self.normal_width = self.width
        self.normal_height = self.height

        def is_hovered(data):
            """
            Wird aufgerufen, wenn die Maus sich bewegt. Testet, ob sie über dem Button ist und reagiert entsprechend.

            :param data: Aktuelle Position der Maus (x, y)
            """
            mouse_x, mouse_y, buttons = data  # buttons zeigt den gedrückten knopf: Links=1, Rad=2, Rechts=4
            if buttons is False and x_px <= int(mouse_x) <= x_px+width_px and y_px <= int(mouse_y) <= y_px+height_px:  # testet ob Maus über dem Button ist, falls ja wird er gefärbt
                self.color = color_scheme.img_hover
                return True
            elif buttons is False:  # elif verhindert, dass gehaltene Knöpfe überschrieben werden
                self.color = (255, 255, 255)  # Bild ist standardmäßig normal
                return False

        def button_clicked(data):
            """
            Wird aufgerufen, wenn ein Maus-Button gedrückt wird. Testet, ob sie über dem Button ist und reagiert entsprechend.

            :param data: Aktueller Zustand und aktuelle Position der Maus (bool, x, y, buttons)
            """
            mouse_state, mouse_x, mouse_y, buttons = data  # buttons zeigt den gedrückten knopf: Links=1, Rad=2, Rechts=4
            if mouse_state is True and buttons == 1 and x_px <= int(mouse_x) <= x_px+width_px and y_px <= int(mouse_y) <= y_px+height_px:
                self.color = color_scheme.img_click
                self.clicked.on_next(True)  # gibt dem clicked-event mit, dass der Button geklickt wurde
                return True
            else:  # falls nicht geclickt wird wird getestet, ob gehovert wird
                is_hovered((mouse_x, mouse_y, mouse_state))
                return False

        # erstellt Subscriptions, um auf Events reagieren zu können, und fängt sie ab
        self._subs = CompositeDisposable([
            events.size.subscribe(lambda _: self.resize(x, y, width, height, events.size.value, color_scheme)),
            events.mouse.subscribe(is_hovered),
            events.mouse_button.subscribe(button_clicked),
        ])

        # eigenes Event des Buttons, welches abfängt, wenn der Button gedrückt wird
        self.clicked = Subject()


class Sprite(pyglet.sprite.Sprite, UIElement):
    def __init__(self, path, x, y, width, height, events, batch=None, group=pyglet.graphics.Group(order=0)):
        """
        Rechteckiges Element mit einem Bild als Fläche. Nicht klckbar.
        pyglet.sprite.Sprite wird erweitert, da es Skalierungs-Methoden hat.

        :param path: Pfad des zu zeichnenden Bildes. Vorzugsweise eine relative Pfadangabe
        :param x: X-Koordinate in %
        :param y: Y-Koordinate in %
        :param width: Breite des Elements in %
        :param height: Höhe des Elements in %
        :param events: events des games
        :param batch: aktueller Pyglet-Batch --> steigert Zeichen-Effizienz
        """

        # konvertiert die Prozentangaben zu Pixeln
        x_px, y_px, width_px, height_px = self.percent_to_pixel(x, y, width, height, events.size.value)

        # zeichnet das Bild in der richtigen Größe
        image = pyglet.image.load(path)
        pyglet.sprite.Sprite.__init__(self, image, x_px, y_px, batch=batch, group=group)

        # speichert die Standard-Maße des Bildes ab
        self.normal_width = self.width
        self.normal_height = self.height

        # skaliert das Bild auf die angegebene Prozentgröße des Fensters
        self.scale_x = width_px / self.normal_width
        self.scale_y = height_px / self.normal_height

        # erstellt Subscriptions, um auf Events reagieren zu können, und fängt sie ab
        self._sub = events.size.subscribe(lambda _: self.resize(x, y, width, height, events.size.value))


class BorderedSpriteButton(pyglet.sprite.Sprite, UIElement):
    def __init__(self, path, x, y, width, height, color_scheme, events, batch=None, group=pyglet.graphics.Group(order=0)):
        """
        Rechteckiger Button mit einem Bild als Fläche und einer Border. Er kann gehovert und geclickt werden.
        pyglet.sprite.Sprite wird erweitert, da es Skalierungs-Methoden hat.

        :param path: Pfad des zu zeichnenden Bildes. Vorzugsweise eine relative Pfadangabe
        :param x: X-Koordinate in %
        :param y: Y-Koordinate in %
        :param width: Breite des Elements in %
        :param height: Höhe des Elements in %
        :param color_scheme: Style-Klasse der Datei color_scheme.py
        :param events: events des games
        :param batch: aktueller Pyglet-Batch --> steigert Zeichen-Effizienz
        """

        # konvertiert die Prozentangaben zu Pixeln
        x_px, y_px, width_px, height_px = self.percent_to_pixel(x, y, width, height, events.size.value)

        # zeichnet ein Rechteck in den Hintergrund, welches die Border ergibt
        self.borderRectangle = pyglet.shapes.Rectangle(x_px, y_px, width_px, height_px,
                                                       color_scheme.border,  # Style wird mitgegeben
                                                       batch=batch, group=group)

        # zeichnet das Bild in der richtigen Größe
        image = pyglet.image.load(path)
        pyglet.sprite.Sprite.__init__(self, image,
                                      x_px + color_scheme.border_thickness,
                                      y_px + color_scheme.border_thickness, batch=batch, group=group)

        # speichert die Standard-Maße des Bildes ab
        self.normal_width = self.width
        self.normal_height = self.height

        # skaliert das Bild auf die angegebene Prozentgröße des Fensters abzüglich der Border
        self.scale_x = (width_px - 2 * color_scheme.border_thickness) / self.width  # skaliert das Bild auf die angegebene Pixelzahl
        self.scale_y = (height_px - 2 * color_scheme.border_thickness) / self.height

        def is_hovered(data):
            """
            Wird aufgerufen, wenn die Maus sich bewegt. Testet, ob sie über dem Button ist und reagiert entsprechend.

            :param data: Aktuelle Position der Maus (x, y)
            """
            mouse_x, mouse_y, buttons = data  # buttons zeigt den gedrückten knopf: Links=1, Rad=2, Rechts=4
            if buttons is False and x_px <= int(mouse_x) <= x_px+width_px and y_px <= int(mouse_y) <= y_px+height_px:  # testet ob Maus über dem Button ist, falls ja wird er gefärbt
                self.color = color_scheme.img_hover
                self.borderRectangle.color = color_scheme.hover_border
                return True
            elif buttons is False:  # elif verhindert, dass gehaltene Knöpfe überschrieben werden
                self.color = (255, 255, 255)  # Bild ist standardmäßig normal
                self.borderRectangle.color = color_scheme.border
                return False

        def button_clicked(data):
            """
            Wird aufgerufen, wenn ein Maus-Button gedrückt wird. Testet, ob sie über dem Button ist und reagiert entsprechend.

            :param data: Aktueller Zustand und aktuelle Position der Maus (bool, x, y, buttons)
            """
            mouse_state, mouse_x, mouse_y, buttons = data  # buttons zeigt den gedrückten knopf: Links=1, Rad=2, Rechts=4
            if mouse_state is True and buttons == 1 and x_px <= int(mouse_x) <= x_px+width_px and y_px <= int(mouse_y) <= y_px+height_px:
                self.color = color_scheme.img_click
                self.borderRectangle.color = color_scheme.click_border
                self.clicked.on_next(True)  # gibt dem clicked-event mit, dass der Button geklickt wurde
                return True
            else:  # falls nicht geclickt wird wird getestet ob gehovert wird
                is_hovered((mouse_x, mouse_y, mouse_state))
                return False

        # eigenes Event des Buttons, welches abfängt, wenn der Button gedrückt wird
        self.clicked = Subject()

        # erstellt Subscriptions, um auf Events reagieren zu können, und fängt sie ab
        self._subs = CompositeDisposable([
            events.size.subscribe(lambda _: self.resize(x, y, width, height, events.size.value, color_scheme)),
            events.mouse.subscribe(is_hovered),
            events.mouse_button.subscribe(button_clicked),
        ])


class BorderedSprite(pyglet.sprite.Sprite, UIElement):
    def __init__(self, path, x, y, width, height, color_scheme, events, batch=None, group=pyglet.graphics.Group(order=0)):
        """
        Rechteckiges Element mit einem Bild als Fläche und einer Border. Nicht klickbar.
        pyglet.sprite.Sprite wird erweitert, da es Skalierungs-Methoden hat.

        :param path: Pfad des zu zeichnenden Bildes. Vorzugsweise eine relative Pfadangabe
        :param x: X-Koordinate in %
        :param y: Y-Koordinate in %
        :param width: Breite des Elements in %
        :param height: Höhe des Elements in %
        :param color_scheme: Style-Klasse der Datei color_scheme.py
        :param events: events des games
        :param batch: aktueller Pyglet-Batch --> steigert Zeichen-Effizienz
        """

        # konvertiert die Prozentangaben zu Pixeln
        x_px, y_px, width_px, height_px = self.percent_to_pixel(x, y, width, height, events.size.value)

        # zeichnet ein Rechteck in den Hintergrund, welches die Border ergibt
        self.borderRectangle = pyglet.shapes.Rectangle(x_px, y_px, width_px, height_px,
                                                       color_scheme.border,  # Style wird mitgegeben
                                                       batch=batch, group=group)

        # zeichnet das Bild in der richtigen Größe
        image = pyglet.image.load(path)
        pyglet.sprite.Sprite.__init__(self, image,
                                      x_px + color_scheme.border_thickness,
                                      y_px + color_scheme.border_thickness, batch=batch, group=group)

        # speichert die Standard-Maße des Bildes ab
        self.normal_width = self.width
        self.normal_height = self.height

        # skaliert das Bild auf die angegebene Prozentgröße des Fensters abzüglich der Border
        self.scale_x = (width_px - 2 * color_scheme.border_thickness) / self.width  # skaliert das Bild auf die angegebene Pixelzahl
        self.scale_y = (height_px - 2 * color_scheme.border_thickness) / self.height

        # erstellt Subscriptions, um auf Events reagieren zu können, und fängt sie ab
        self._sub = events.size.subscribe(lambda _: self.resize(x, y, width, height, events.size.value, color_scheme))


class Gif(pyglet.sprite.Sprite, UIElement):  # lädt ein Gif
    def __init__(self, path, x, y, width, height, duration, loop, events, batch=None, group=pyglet.graphics.Group(order=0)):
        """
        Rechteckiges Element mit einem Gif als Fläche. Nicht klickbar.
        pyglet.sprite.Sprite wird erweitert, da es Skalierungs-Methoden hat.

        :param path: Pfad des zu zeichnenden Bildes. Vorzugsweise eine relative Pfadangabe
        :param x: X-Koordinate in %
        :param y: Y-Koordinate in %
        :param width: Breite des Elements in %
        :param height: Höhe des Elements in %
        :param duration: Dauer in Sekunden, die ein Durchlauf des Gifs dauern soll.
        :param loop: boolean, der angibt, ob das Gif nach dem ersten Durchlauf stoppt oder neu startet
        :param events: events des games
        :param batch: aktueller Pyglet-Batch --> steigert Zeichen-Effizienz
        """

        # konvertiert die Prozentangaben zu Pixeln
        x_px, y_px, width_px, height_px = self.percent_to_pixel(x, y, width, height, events.size.value)

        # erstellt eine Liste der einzelnen Bilder des Gifs
        image = pyglet.image.load_animation(path)
        animation_frames = []
        for frames in image.frames:
            animation_frames.append(frames.__getattribute__("image"))

        # erstellt aus den einzelnen Bildern eine Animation der gewünschten Länge. Loop erlaubt ununterbrochene Wiederholung der Animation
        animation = image.from_image_sequence(animation_frames, duration=duration / len(animation_frames), loop=loop)
        pyglet.sprite.Sprite.__init__(self, animation, x_px, y_px, batch=batch, group=group)

        # speichert die Standard-Maße des Gifs
        self.normal_width = self.width
        self.normal_height = self.height

        # skaliert das Bild auf die angegebene Prozentgröße des Fensters
        self.scale_x = width_px / self.normal_width
        self.scale_y = height_px / self.normal_height

        # erstellt Subscriptions, um auf Events reagieren zu können, und fängt sie ab
        self._sub = events.size.subscribe(lambda _: self.resize(x, y, width, height, events.size.value))
        self.loop_finished = Subject()

    def on_animation_end(self):
        self.loop_finished.on_next(True)


class GifButton(pyglet.sprite.Sprite, UIElement):
    def __init__(self, path, x, y, width, height, duration, loop, events, batch=None, group=pyglet.graphics.Group(order=0)):
        """
        Rechteckiger Button mit einem Gif als Fläche. Kann geklickt werden..
        pyglet.sprite.Sprite wird erweitert, da es Skalierungs-Methoden hat.

        :param path: Pfad des zu zeichnenden Bildes. Vorzugsweise eine relative Pfadangabe
        :param x: X-Koordinate in %
        :param y: Y-Koordinate in %
        :param width: Breite des Elements in %
        :param height: Höhe des Elements in %
        :param duration: Dauer in Sekunden, die ein Durchlauf des Gifs dauern soll.
        :param loop: boolean, der angibt, ob das Gif nach dem ersten Durchlauf stoppt oder neu startet
        :param events: events des games
        :param batch: aktueller Pyglet-Batch --> steigert Zeichen-Effizienz
        """

        # konvertiert die Prozentangaben zu Pixeln
        x_px, y_px, width_px, height_px = self.percent_to_pixel(x, y, width, height, events.size.value)

        # erstellt eine Liste der einzelnen Bilder des Gifs
        image = pyglet.image.load_animation(path)
        animation_frames = []
        for frames in image.frames:
            animation_frames.append(frames.__getattribute__("image"))

        # erstellt aus den einzelnen Bildern eine Animation der gewünschten Länge. Loop erlaubt ununterbrochene Wiederholung der Animation
        animation = image.from_image_sequence(animation_frames, duration=duration / len(animation_frames), loop=loop)
        pyglet.sprite.Sprite.__init__(self, animation, x_px, y_px, batch=batch, group=group)

        # speichert die Standard-Maße des Gifs
        self.normal_width = self.width
        self.normal_height = self.height

        # skaliert das Bild auf die angegebene Prozentgröße des Fensters
        self.scale_x = width_px / self.normal_width
        self.scale_y = height_px / self.normal_height

        def button_clicked(data):
            """
            Wird aufgerufen, wenn ein Maus-Button gedrückt wird. Testet, ob sie über dem Button ist und reagiert entsprechend.

            :param data: Aktueller Zustand und aktuelle Position der Maus (bool, x, y, buttons)
            """
            mouse_state, mouse_x, mouse_y, buttons = data  # buttons zeigt den gedrückten knopf: Links=1, Rad=2, Rechts=4
            if mouse_state is True and buttons == 1 and self.x_px <= int(mouse_x) <= self.x_px+self.width_px and self.y_px <= int(mouse_y) <= self.y_px+self.height_px:
                self.clicked.on_next(True)  # gibt dem clicked-event mit, dass der Button geklickt wurde
                return True
            else:  # falls nicht geklickt
                return False

        # erstellt Subscriptions, um auf Events reagieren zu können, und fängt sie ab
        self._sub = CompositeDisposable([
            events.size.subscribe(lambda _: self.resize(x, y, width, height, events.size.value)),
            events.mouse_button.subscribe(button_clicked),
        ])

        # eigenes Event des Buttons, welches abfängt, wenn der Button gedrückt wird
        self.clicked = Subject()
        self.loop_finished = Subject()

    def on_animation_end(self):
        self.loop_finished.on_next(True)

    def dispose(self) -> None:
        self.delete()
        super().dispose()