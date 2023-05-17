import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable

from controller import Screen


class StatisticsScreen(Screen):
    def __init__(self, events, save):
        super().__init__()
        if save == 0: save_text = "Alle Spielstände"
        else: save_text = "Spielstand " + str(save)

        self.batch = pyglet.graphics.Batch()
        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        background = pyglet.graphics.Group(order=-1)
        foreground = pyglet.graphics.Group(order=1)

        # Layout für den Statistik-Bildschirm
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, self.batch)
        self.header = ui_elements.BorderedRectangle("Statistiken", 20, 75, 60, 20, events.color_scheme, color_scheme.Minecraft, 4, events, self.batch)
        self.current_stats = ui_elements.BorderedRectangle(save_text, 20, 62.5, 60, 10, events.color_scheme, color_scheme.Minecraft, 4, events, self.batch)
        self.back = ui_elements.InputButton("Zurück", 20, 50, 60, 10, events.color_scheme, color_scheme.Minecraft, 4, events, self.batch)

        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        from main_controller import PopScreen
        self._subs.add(self.back.clicked.subscribe(lambda _: self.game_command.on_next(PopScreen())))

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
