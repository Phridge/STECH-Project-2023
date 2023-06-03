import contextlib

import pygame
import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable
from pygame import mixer

from controller import Screen
from controller.story_mode.level2_screen import Level2Screen
from controller.story_mode.level3_screen import Level3Screen
from controller.story_mode.level4_screen import Level4Screen


# from controller.story_mode.level5_screen import Level5Screen


class LevelFinishedScreen(Screen):
    def __init__(self, events, save_file, next_screen, points):
        super().__init__()
        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        background = pyglet.graphics.Group(order=-1)
        foreground = pyglet.graphics.Group(order=1)

        # Erstes Layout für den HomeScreen
        # self.background = pyglet.shapes.Rectangle(0, 0, 100, 100, (0, 0, 0), self.batch, background)


        self.header = ui_elements.BorderedRectangle("Level Abgeschlossen!", 20, 75, 60, 20, events.color_scheme, color_scheme.Minecraft, 5, events, self.batch)
        self.points_achieved = ui_elements.BorderedRectangle(str(points), 35, 55, 30, 15, events.color_scheme, color_scheme.Minecraft, 7, events, self.batch)

        self.back = ui_elements.InputButton("Modus verlassen", 15, 10, 20, 10, events.color_scheme, color_scheme.Minecraft, 7, events, self.batch)
        self.statistics = ui_elements.InputButton("Auswertung", 40, 10, 20, 10, events.color_scheme, color_scheme.Minecraft, 8.4, events, self.batch)
        self.next_level = ui_elements.InputButton("Nächstes Level", 65, 10, 20, 10, events.color_scheme, color_scheme.Minecraft, 7, events, self.batch)

        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        from controller.story_mode.main_screen import MainStoryScreen

        self._subs.add(self.back.clicked.subscribe(lambda _: self.push_screen(MainStoryScreen.init_fn(save_file))))
        self._subs.add(self.next_level.clicked.subscribe(lambda _: self.push_next_level(next_screen, save_file)))
        self._subs.add(self.statistics.clicked.subscribe(lambda _: print("AHHHHHHH HIER KOMMEN MARTINS STATS")))

        self.play_music()

    def push_next_level(self, next_screen, save_file):
        pass
        match next_screen:
            case "Level2":
                self.push_screen(Level2Screen.init_fn(save_file))
            case "Level3":
                self.push_screen(Level3Screen.init_fn(save_file))
            case "Level4":
                self.push_screen(Level4Screen.init_fn(save_file))
            #case "Level5":
                #self.push_screen(Level5Screen.init_fn(save_file))

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch

    def play_music(self):
        with contextlib.suppress(pygame.error):
            mixer.init()
            mixer.music.load("assets/sounds/02 Start Menu.mp3")
            mixer.music.play()
            mixer.music.play(-1)
