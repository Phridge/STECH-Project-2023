import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable

from controller import Screen


class ErrorScreen(Screen):
    def __init__(self, events):
        super().__init__()
        self.batch = pyglet.graphics.Batch()
        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        background = pyglet.graphics.Group(order=-1)
        foreground = pyglet.graphics.Group(order=1)

        # Erstes Layout für den Error-Bildschirm
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, self.batch)
        self.gif = ui_elements.Gif("assets/images/popcat.gif", 35, 5, 30, 30, 0.5, True, events, self.batch)
        self.header = ui_elements.BorderedRectangle("Es liegt ein Fehler vor :(", 20, 75, 60, 20, events.color_scheme, color_scheme.Minecraft, 4, events, self.batch)
        self.restart_button = ui_elements.InputButton("Neu Starten", 35, 55, 30, 10, events.color_scheme, color_scheme.Minecraft, 6, events, self.batch)
        self.end_button = ui_elements.InputButton("Spiel beenden", 35, 37.5, 30, 10, events.color_scheme, color_scheme.Minecraft, 6, events, self.batch)

        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        self._subs.add(self.restart_button.clicked.subscribe(lambda _: self.restart(True)))
        self._subs.add(self.end_button.clicked.subscribe(lambda _: self.restart(False)))

    def restart(self, data):  # Wird getriggert, wenn ein Spielstand ausgewählt wird
        self.change_controller.on_next(("Restart", data))

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
