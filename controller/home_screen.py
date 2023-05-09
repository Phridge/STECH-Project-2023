import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable
from pygame import mixer

from controller import Screen


class HomeScreen(Screen):
    def __init__(self, events, save_file):
        super().__init__()
        self.batch = pyglet.graphics.Batch()
        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        background = pyglet.graphics.Group(order=-1)
        foreground = pyglet.graphics.Group(order=1)

        # Erstes Layout für den HomeScreen
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, self.batch)

        self.header = ui_elements.BorderedRectangle("HomeScreen von Save " + str(save_file), 20, 75, 60, 20, events.color_scheme, color_scheme.Minecraft, 5, events, self.batch)
        self.learning_mode = ui_elements.InputButton("Lern-Modus", 25, 55, 50, 10, events.color_scheme, color_scheme.Minecraft, 4, events, self.batch)
        self.story_mode = ui_elements.InputButton("Story-Modus", 25, 42.5, 50, 10, events.color_scheme, color_scheme.Minecraft, 4, events, self.batch)
        self.sandbox_mode = ui_elements.InputButton("Sandbox-Modus", 25, 30, 50, 10, events.color_scheme, color_scheme.Minecraft, 4, events, self.batch)

        self.settings = ui_elements.InputButton("Einstellungen", 2.5, 85, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 8, events, self.batch)
        self.statistics = ui_elements.InputButton("Statistiken", 85, 85, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 8.4, events, self.batch)
        self.back = ui_elements.InputButton("Zurück", 40, 10, 20, 10, events.color_scheme, color_scheme.Minecraft, 10, events, self.batch)

        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        self._subs.add(self.back.clicked.subscribe(lambda _: self.change_screen("StartScreen", save_file)))
        self._subs.add(self.learning_mode.clicked.subscribe(lambda _: self.change_screen("MainLearningScreen", save_file)))
        self._subs.add(self.story_mode.clicked.subscribe(lambda _: self.change_screen("MainStoryScreen", save_file)))
        self._subs.add(self.sandbox_mode.clicked.subscribe(lambda _: self.change_screen("MainSandboxScreen", save_file)))
        self._subs.add(self.settings.clicked.subscribe(lambda _: self.change_screen("Settings", save_file)))
        self._subs.add(self.statistics.clicked.subscribe(lambda _: self.change_screen("Statistics", save_file)))

        self.play_music()

    def change_screen(self, new_screen, save):  # Wird getriggert, wenn man zurück zum Hauptmenü will
        # save suchen und auswählen
        self.change_controller.on_next((new_screen, save))

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch

    def play_music(self):
        mixer.init()
        mixer.music.load("assets/sounds/02 Start Menu.mp3")
        mixer.music.play()
        mixer.music.play(-1)
