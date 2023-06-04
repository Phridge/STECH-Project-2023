import contextlib

import pygame
import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable
from pygame import mixer

from controller import Screen
from controller.learning_mode.main_screen import MainLearningScreen
from controller.sandbox_mode.sandbox_level import SandboxLevel
from controller.settings import SettingsScreen
from controller.statistics import StatisticsScreen
#import statistic_lib.statistic_view as SV
from controller.story_mode.main_screen import MainStoryScreen
from tools import save_and_open


class HomeScreen(Screen):
    def __init__(self, events, save_file):
        super().__init__()
        self.batch = pyglet.graphics.Batch()
        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter
        # ist alles. Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        background = pyglet.graphics.Group(order=-1)
        foreground = pyglet.graphics.Group(order=1)

        # Erstes Layout für den HomeScreen
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events,
                                             self.batch)

        self.header = ui_elements.BorderedRectangle("HomeScreen von Save " + str(save_file), 20, 75, 60, 20,
                                                    events.color_scheme, color_scheme.Minecraft, 5, events, self.batch)
        self.learning_mode = ui_elements.InputButton("Lern-Modus", 25, 55, 50, 10, events.color_scheme,
                                                     color_scheme.Minecraft, 4, events, self.batch)
        self.story_mode = ui_elements.InputButton("Story-Modus", 25, 42.5, 50, 10, events.color_scheme,
                                                  color_scheme.Minecraft, 4, events, self.batch)
        self.sandbox_mode = ui_elements.InputButton("Sandbox-Modus", 25, 30, 50, 10, events.color_scheme,
                                                    color_scheme.Minecraft, 4, events, self.batch)

        self.settings = ui_elements.InputButton("Einstellungen", 2.5, 85, 12.5, 10, events.color_scheme,
                                                color_scheme.Minecraft, 8, events, self.batch)
        self.statistics = ui_elements.InputButton("Statistiken", 85, 85, 12.5, 10, events.color_scheme,
                                                  color_scheme.Minecraft, 8.4, events, self.batch)
        self.back = ui_elements.InputButton("Zurück", 40, 10, 20, 10, events.color_scheme, color_scheme.Minecraft, 10,
                                            events, self.batch)

        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        from main_controller import PushScreen, PopScreen
        def goto(screen_init):
            return lambda _: self.game_command.on_next(PushScreen(screen_init))

        self._subs.add(self.back.clicked.subscribe(lambda _: self.load_settings(0)))
        self._subs.add(self.back.clicked.subscribe(lambda _: self.game_command.on_next(PopScreen())))
        self._subs.add(self.learning_mode.clicked.subscribe(goto(MainLearningScreen.init_fn(save_file))))
        self._subs.add(self.story_mode.clicked.subscribe(goto(MainStoryScreen.init_fn(save_file))))
        self._subs.add(self.sandbox_mode.clicked.subscribe(goto(SandboxLevel.init_fn(save_file))))
        self._subs.add(self.settings.clicked.subscribe(goto(SettingsScreen.init_fn(save_file))))

        self._subs.add(self.statistics.clicked.subscribe(goto(StatisticsScreen.init_fn(save_file))))
        #self._subs.add(self.statistic_lib.clicked.subscribe(goto(SV)))

        self.play_music()

    def load_settings(self, save):
        """
        Lädt die Settings des angegebenen Saves
        :param save: Zu ladender Save, hier Save 0
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

    def play_music(self):
        with contextlib.suppress(pygame.error):
            mixer.init()
            mixer.music.load("assets/sounds/02 Start Menu.mp3")
            mixer.music.play(-1)
