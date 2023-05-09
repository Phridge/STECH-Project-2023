import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable
from pygame import mixer


from controller import Screen


class StartScreen(Screen):
    def __init__(self, events):
        super().__init__()
        self.batch = pyglet.graphics.Batch()
        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        # einfach foreground oder background als zusätzliche Variable ans Element packen
        background = pyglet.graphics.Group(order=-1)
        foreground= pyglet.graphics.Group(order=1)

        # Erstes Layout für den Hauptbildschirm
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, self.batch)
        self.header = ui_elements.BorderedRectangle("Die Maschinen-Revolution", 20, 75, 60, 20, events.color_scheme, color_scheme.Minecraft, 4.5, events, self.batch)
        self.save1 = ui_elements.InputButton("Erster Spielstand", 35, 55, 30, 10, events.color_scheme, color_scheme.Minecraft, 5.5, events, self.batch)
        self.save2 = ui_elements.InputButton("Zweiter Spielstand", 35, 42.5, 30, 10, events.color_scheme, color_scheme.Minecraft, 5.5, events, self.batch)
        self.save3 = ui_elements.InputButton("Dritter Spielstand", 35, 30, 30, 10, events.color_scheme, color_scheme.Minecraft, 5.5, events, self.batch)
        self.delete_save1 = ui_elements.InputButton("Neu 1", 67.5, 55, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 16, events, self.batch)
        self.delete_save2 = ui_elements.InputButton("Neu 2", 67.5, 42.5, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 16, events, self.batch)
        self.delete_save3 = ui_elements.InputButton("Neu 3", 67.5, 30, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 16, events, self.batch)
        self.info = ui_elements.BorderedRectangle("Hinweis: Gib mal \"Erster Spielstand\" auf der Tastatur ein!", 10, 17.5, 80, 10, events.color_scheme, color_scheme.Minecraft, 1.9, events, self.batch)

        self.leave = ui_elements.InputButton("Verlassen", 40, 2.5, 20, 10, events.color_scheme, color_scheme.Minecraft, 7, events, self.batch)
        self.settings = ui_elements.InputButton("Einstellungen", 2.5, 85, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 8, events, self.batch)
        self.statistics = ui_elements.InputButton("Statistiken", 85, 85, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 8.4, events, self.batch)

        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        self._subs.add(self.save1.clicked.subscribe(lambda _: self.change_screen("HomeScreen", 1)))
        self._subs.add(self.save2.clicked.subscribe(lambda _: self.change_screen("HomeScreen", 2)))
        self._subs.add(self.save3.clicked.subscribe(lambda _: self.change_screen("HomeScreen", 3)))
        self._subs.add(self.delete_save1.clicked.subscribe(lambda _: self.change_screen("DeleteSaveScreen", 1)))
        self._subs.add(self.delete_save2.clicked.subscribe(lambda _: self.change_screen("DeleteSaveScreen", 2)))
        self._subs.add(self.delete_save3.clicked.subscribe(lambda _: self.change_screen("DeleteSaveScreen", 3)))
        self._subs.add(self.settings.clicked.subscribe(lambda _: self.change_screen("Settings", 0)))
        self._subs.add(self.statistics.clicked.subscribe(lambda _: self.change_screen("Statistics", 0)))
        self._subs.add(self.leave.clicked.subscribe(lambda _: self.change_screen("Restart", False)))

        self.play_music(events.volume)

    def change_screen(self, new_screen, save):  # Wird getriggert, wenn man zurück zum Hauptmenü will
        # save suchen und auswählen
        self.change_controller.on_next((new_screen, save))

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch


    def play_music(self, volume):
        mixer.init()
        mixer.music.load("assets/sounds/02 Start Menu.mp3")
        mixer.music.play()
        mixer.music.play(-1)
        mixer.music.set_volume(volume)

