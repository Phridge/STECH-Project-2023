import pyglet
import pygame
import contextlib

import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable

from controller import Controller, Screen
from controller.settings import SettingsScreen
from controller.statistics import StatisticsScreen
from controller.story_mode.level1_screen import Level1Screen
from tools import save_and_open


class MainStoryScreen(Screen):
    def __init__(self, events, save):
        super().__init__()
        self.batch = pyglet.graphics.Batch()
        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        background = pyglet.graphics.Group(order=-1)
        foreground = pyglet.graphics.Group(order=1)

        self.story_progress = save_and_open.get_story_progress(save)

        # Layout für den Startbildschirm des Lern-Modus
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, self.batch, background)
        self.header = ui_elements.BorderedRectangle("Story", 20, 75, 60, 20, events.color_scheme, color_scheme.Minecraft, 4, events, self.batch)

        self.back = ui_elements.InputButton("Zurück", 40, 10, 20, 10, events.color_scheme, color_scheme.Minecraft, 10, events, self.batch)
        self.settings = ui_elements.InputButton("Einstellungen", 2.5, 85, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 8, events, self.batch)
        self.statistics = ui_elements.InputButton("Statistiken", 85, 85, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 8.4, events, self.batch)

        self.level1_button = ui_elements.BorderedSpriteButton("assets/images/port.gif", 2.5, 45, 15, 15, events.color_scheme, events, self.batch)
        self.level1_label = ui_elements.InputButton("Erstes Level", 2.5, 32.5, 15, 10, events.color_scheme, color_scheme.Minecraft, 8, events, self.batch)
        if self.story_progress >= 0: # SOLLTE EIGENTLICH 1 SEIN; IST NUR 0 DAMIT ES TROTZ BUGS SPIELBAR IST Level 2 nur spielbar wenn Level 1 bereits abgeschlossen wurde
            self.level2_button = ui_elements.BorderedSpriteButton("assets/images/forest.gif", 22.5, 45, 15, 15, events.color_scheme, events, self.batch)
            self.level2_label = ui_elements.InputButton("Zweites Level", 22.5, 32.5, 15, 10, events.color_scheme, color_scheme.Minecraft, 8, events, self.batch)
        else:
            self.level2_button = ui_elements.BorderedSprite("assets/images/forest.gif", 22.5, 45, 15, 15, events.color_scheme, events, self.batch)
            self.level2_label = ui_elements.BorderedRectangle("Gesperrt", 22.5, 32.5, 15, 10, events.color_scheme, color_scheme.Minecraft, 8, events, self.batch)

        if self.story_progress >= 0: # SOLLTE EIGENTLICH 2 SEIN; IST NUR 0 DAMIT ES TROTZ BUGS SPIELBAR IST Level 3 nur spielbar wenn Level 2 bereits abgeschlossen wurde
            self.level3_button = ui_elements.BorderedSpriteButton("assets/images/city.gif", 42.5, 45, 15, 15, events.color_scheme, events, self.batch)
            self.level3_label = ui_elements.InputButton("Drittes Level", 42.5, 32.5, 15, 10, events.color_scheme, color_scheme.Minecraft, 8, events, self.batch)
        else:
            self.level3_button = ui_elements.BorderedSprite("assets/images/city.gif", 42.5, 45, 15, 15, events.color_scheme, events, self.batch)
            self.level3_label = ui_elements.BorderedRectangle("Gesperrt", 42.5, 32.5, 15, 10, events.color_scheme, color_scheme.Minecraft, 8, events, self.batch)

        self.under_development = ui_elements.BorderedRectangle("In der Entwicklung", 65, 35, 30, 22.5, events.color_scheme, color_scheme.Minecraft, 4.5, events, self.batch, foreground)
        self.level4_button = ui_elements.BorderedSprite("assets/images/bridge.gif", 62.5, 45, 15, 15, events.color_scheme, events, self.batch)
        self.level4_label = ui_elements.BorderedRectangle("Viertes Level", 62.5, 32.5, 15, 10, events.color_scheme, color_scheme.Minecraft, 8, events, self.batch)
        self.level5_button = ui_elements.BorderedSprite("assets/images/city.gif", 82.5, 45, 15, 15, events.color_scheme, events, self.batch)
        self.level5_label = ui_elements.BorderedRectangle("Fünftes Level", 82.5, 32.5, 15, 10, events.color_scheme, color_scheme.Minecraft, 8, events, self.batch)

        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        self._subs.add(self.back.clicked.subscribe(lambda _: self.go_back()))
        self._subs.add(self.settings.clicked.subscribe(lambda _: self.push_screen(SettingsScreen.init_fn(save))))
        self._subs.add(self.statistics.clicked.subscribe(lambda _: self.push_screen(StatisticsScreen.init_fn(save))))

        from controller.story_mode.level1_screen import Level1Screen
        from controller.story_mode.level2_screen import Level2Screen
        from controller.story_mode.level3_screen import Level3Screen
        from controller.story_mode.level4_screen import Level4Screen
        # from controller.story_mode.level5_screen import Level5Screen

        self._subs.add(self.level1_button.clicked.subscribe(lambda _: self.reload_screen(Level1Screen.init_fn(save))))
        self._subs.add(self.level1_label.clicked.subscribe(lambda _: self.reload_screen(Level1Screen.init_fn(save))))
        if self.story_progress >= 0: # SOLLTE EIGENTLICH 1 SEIN; IST NUR 0 DAMIT ES TROTZ BUGS SPIELBAR IST
            self._subs.add(self.level2_button.clicked.subscribe(lambda _: self.reload_screen(Level2Screen.init_fn(save))))
            self._subs.add(self.level2_label.clicked.subscribe(lambda _: self.reload_screen(Level2Screen.init_fn(save))))
        if self.story_progress >= 0: # SOLLTE EIGENTLICH 2 SEIN; IST NUR 0 DAMIT ES TROTZ BUGS SPIELBAR IST
            self._subs.add(self.level3_button.clicked.subscribe(lambda _: self.reload_screen(Level3Screen.init_fn(save))))
            self._subs.add(self.level3_label.clicked.subscribe(lambda _: self.reload_screen(Level3Screen.init_fn(save))))
        # self._subs.add(self.level4_button.clicked.subscribe(lambda _: self.reload_screen(Level4Screen.init_fn(save))))
        # self._subs.add(self.level4_label.clicked.subscribe(lambda _: self.reload_screen(Level4Screen.init_fn(save))))
        # self._subs.add(self.level5_button.clicked.subscribe(lambda _: self.reload_screen(Level5Screen.init_fn())))
        # self._subs.add(self.level5_label.clicked.subscribe(lambda _: self.reload_screen(Level5Screen.init_fn())))


    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
