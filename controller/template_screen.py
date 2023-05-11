import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable

from controller import Screen

"""
Eine Vorlage für einen Screen. ab Zeile 22 können Elemente eingefügt werde. Ein paar der ui-Elements sind als Beispiel gezeigt.
In dieser Datei sind nur die absoluten Essentials drin. Hinzufügen ist kein Problem, löschen schon.
Lasst euch dieses Template anzeigen, indem ihr es im main_controller als initialen Controller setzt :D
"""


class TemplateScreen(Screen):
    def __init__(self, events):
        super().__init__()
        self.batch = pyglet.graphics.Batch()
        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        background = pyglet.graphics.Group(order=-1)
        foreground = pyglet.graphics.Group(order=1)

        # im folgenden Block können Elemente eingefügt werden. Die Elemente die schon da sind dienen nur als Beispiele
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, self.batch)
        self.header = ui_elements.InputButton("Die Maschinen-Revolution", 20, 75, 60, 20, events.color_scheme, color_scheme.Minecraft, 5, events, self.batch)
        # self.gif = ui_elements.Gif("assets/images/popcat.gif", 35, 42.5, 30, 10, 1, True, events, self.batch)
        self.button1 = ui_elements.BorderedRectangleButton("Spielstand 1", 35, 55, 30, 10, events.color_scheme, color_scheme.Minecraft, 6, events, self.batch)
        # self.button2 = ui_elements.GifButton("assets/images/popcat.gif", 35, 30, 30, 10, 1, True, events, self.batch)
        self.button3 = ui_elements.BorderedSpriteButton("assets/images/popcat.png", 35, 17.5, 30, 10, events.color_scheme, events, self.batch)

        # Hier muss für jeden Button eine Subscription erstellt werden.
        # In der Lambda-Funktion wird dann die Funktion angebgeben, die aufgerufen werden soll wenn der jeweilige Button gedrückt wird
        self._subs.add(self.button1.clicked.subscribe(lambda _: self.button_clicked(1)))
        # self._subs.add(self.button2.clicked.subscribe(lambda _: self.button_clicked(2)),)
        self._subs.add(self.header.clicked.subscribe(lambda _: self.button_clicked(2)))
        self._subs.add(self.button3.clicked.subscribe(lambda _: self.button_clicked(3)))

    #  Falls die Funktionen namentlich nicht passen erstellte einfach neue!
    def button_clicked(self, data):  # Wird getriggert, wenn ein Spielstand ausgewählt wird
        self.change_controller.on_next(("HomeScreen", data))

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
