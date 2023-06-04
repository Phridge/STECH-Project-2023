import contextlib

import pygame
import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable
from pygame import mixer


from controller import Screen
from controller.delete_save_screen import DeleteSaveScreen
from controller.home_screen import HomeScreen
from controller.settings import SettingsScreen
from controller.statistics import StatisticsScreen
from controller.user_documentation import UserDocumentationScreen
from tools import save_and_open


class StartScreen(Screen):
    def __init__(self, events):
        super().__init__()
        self.batch = pyglet.graphics.Batch()
        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        # einfach foreground oder background als zusätzliche Variable ans Element packen
        background = pyglet.graphics.Group(order=-1)
        foreground = pyglet.graphics.Group(order=1)

        #Layout für den Hauptbildschirm
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, self.batch)
        self.header = ui_elements.BorderedRectangle("Typerpunk: The Rise of Maxwell", 20, 75, 60, 20, events.color_scheme, color_scheme.Minecraft, 3.5, events, self.batch)
        self.save1 = ui_elements.InputButton("Erster Spielstand", 35, 55, 30, 10, events.color_scheme, color_scheme.Minecraft, 5.5, events, self.batch)
        self.save2 = ui_elements.InputButton("Zweiter Spielstand", 35, 42.5, 30, 10, events.color_scheme, color_scheme.Minecraft, 5.5, events, self.batch)
        self.save3 = ui_elements.InputButton("Dritter Spielstand", 35, 30, 30, 10, events.color_scheme, color_scheme.Minecraft, 5.5, events, self.batch)
        self.delete_save1 = ui_elements.InputButton("Neu 1", 67.5, 55, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 16, events, self.batch)
        self.delete_save2 = ui_elements.InputButton("Neu 2", 67.5, 42.5, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 16, events, self.batch)
        self.delete_save3 = ui_elements.InputButton("Neu 3", 67.5, 30, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 16, events, self.batch)
        self.info = ui_elements.BorderedRectangle("Hinweis: Gib mal \"Erster Spielstand\" auf der Tastatur ein!", 10, 17.5, 80, 10, events.color_scheme, color_scheme.Minecraft, 1.9, events, self.batch)

        self.leave = ui_elements.InputButton("Verlassen", 40, 2.5, 20, 10, events.color_scheme, color_scheme.Minecraft, 8, events, self.batch)
        self.settings = ui_elements.InputButton("Einstellungen", 2.5, 85, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 8, events, self.batch)
        self.help = ui_elements.InputButton("Hilfe", 85, 85, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 12, events, self.batch)
        # self.statistics = ui_elements.InputButton("Statistiken", 85, 85, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 8.4, events, self.batch)

        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        from main_controller import PushScreen, Exit
        def goto(screen_init):
            return lambda _: self.game_command.on_next(PushScreen(screen_init))

        self._subs.add(self.save1.clicked.subscribe(lambda _: self.load_settings(1)))
        self._subs.add(self.save1.clicked.subscribe(goto(HomeScreen.init_fn(1))))
        self._subs.add(self.save2.clicked.subscribe(lambda _: self.load_settings(2)))
        self._subs.add(self.save2.clicked.subscribe(goto(HomeScreen.init_fn(2))))
        self._subs.add(self.save3.clicked.subscribe(lambda _: self.load_settings(3)))
        self._subs.add(self.save3.clicked.subscribe(goto(HomeScreen.init_fn(3))))
        self._subs.add(self.delete_save1.clicked.subscribe(goto(DeleteSaveScreen.init_fn(1))))
        self._subs.add(self.delete_save2.clicked.subscribe(goto(DeleteSaveScreen.init_fn(2))))
        self._subs.add(self.delete_save3.clicked.subscribe(goto(DeleteSaveScreen.init_fn(3))))
        self._subs.add(self.settings.clicked.subscribe(goto(SettingsScreen.init_fn(0))))
        # self._subs.add(self.statistics.clicked.subscribe(goto(StatisticsScreen.init_fn(0))))
        self._subs.add(self.leave.clicked.subscribe(lambda _: self.game_command.on_next(Exit())))
        self._subs.add(self.help.clicked.subscribe(goto(UserDocumentationScreen.init_fn())))

        self.play_music(events.volume)

    def load_settings(self, save):
        """
        Lädt die Settings aus der Datenbank, wenn vom StartScreen in die einzelnen Saves manövriert wird
        :param save: Spielstand, dessen Einstellungen geladen werden sollen
        """
        from main_controller import ChangeSetting, SetFullscreen
        if save_and_open.get_settings(save):
            fullscreen, volume, color, size = save_and_open.get_settings(save)
            print((fullscreen, volume, color, size))
            self.game_command.on_next(ChangeSetting("color_scheme", color))
            self.game_command.on_next(SetFullscreen(fullscreen))
            self.game_command.on_next(ChangeSetting("volume", volume))
            if size: self.game_command.on_next(ChangeSetting("size", size))

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch


    def play_music(self, volume): #Musik im Start Menü
        with contextlib.suppress(pygame.error):
            mixer.music.load("assets/sounds/02 Start Menu.mp3")
            mixer.music.play()
            mixer.music.play(-1)

