import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable

from controller import Controller, Screen


class MainStoryScreen(Screen):
    def __init__(self, events, save):
        super().__init__()
        self.batch = pyglet.graphics.Batch()
        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        background = pyglet.graphics.Group(order=-1)
        foreground = pyglet.graphics.Group(order=1)

        # Layout für den Startbildschirm des Lern-Modus
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, self.batch)
        self.header = ui_elements.BorderedRectangle("Story", 20, 75, 60, 20, events.color_scheme, color_scheme.Minecraft, 4, events, self.batch)

        self.back = ui_elements.InputButton("Zurück", 40, 10, 20, 10, events.color_scheme, color_scheme.Minecraft, 10, events, self.batch)
        self.settings = ui_elements.InputButton("Einstellungen", 2.5, 85, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 8, events, self.batch)
        self.statistics = ui_elements.InputButton("Statistiken", 85, 85, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 8.4, events, self.batch)

        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        self._subs.add(self.back.clicked.subscribe(lambda _: self.change_screen("HomeScreen", save)))
        self._subs.add(self.settings.clicked.subscribe(lambda _: self.change_screen("Settings", save)))
        self._subs.add(self.statistics.clicked.subscribe(lambda _: self.change_screen("Statistics", save)))

    def change_screen(self, new_screen, save):  # Wird getriggert, wenn man zurück zum Hauptmenü will
        # save suchen und auswählen
        self.change_controller.on_next((new_screen, save))

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
