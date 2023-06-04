import contextlib

import pygame
import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable
from pygame import mixer

from controller import Screen
from tools import save_and_open


class LevelFinishedScreen(Screen):
    def __init__(self, events, save_file, previous_screen, points, successful):
        super().__init__()
        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        background = pyglet.graphics.Group(order=-1)
        foreground = pyglet.graphics.Group(order=1)

        # Erstes Layout für den HomeScreen
        self.background = ui_elements.Sprite("assets/images/tearoom.png", 0, 0, 100, 100, events, self.batch, background)
        self.maxwell = ui_elements.Sprite("assets/images/mech_tea.png", 40, 17.5, 20, 37.5, events, self.batch)

        if successful:  headline = "Level abgeschlossen!"
        else: headline = "Level fehlgeschlagen"
        self.header = ui_elements.BorderedRectangle(headline, 20, 75, 60, 20, events.color_scheme, color_scheme.Minecraft, 5, events, self.batch)
        self.back = ui_elements.InputButton("Level verlassen", 15, 5, 20, 10, events.color_scheme, color_scheme.Minecraft, 7, events, self.batch)
        self.statistics = ui_elements.InputButton("Auswertung", 40, 5, 20, 10, events.color_scheme, color_scheme.Minecraft, 8.4, events, self.batch)

        if successful:
            self.points_achieved = ui_elements.BorderedRectangle(str(points) + " Punkte", 35, 55, 30, 15, events.color_scheme, color_scheme.Minecraft, 7, events, self.batch)
            self.next_level = ui_elements.InputButton("Nächstes Level", 65, 5, 20, 10, events.color_scheme, color_scheme.Minecraft, 7, events, self.batch)
            save_and_open.set_level_progress(save_file, previous_screen)
        else:
            self.retry = ui_elements.InputButton("Neuer Versuch", 65, 5, 20, 10, events.color_scheme, color_scheme.Minecraft, 7, events, self.batch)


        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        from controller.story_mode.main_screen import MainStoryScreen

        self._subs.add(self.back.clicked.subscribe(lambda _: self.reload_screen(MainStoryScreen.init_fn(save_file))))
        self._subs.add(self.statistics.clicked.subscribe(lambda _: print("AHHHHHHH HIER KOMMEN MARTINS STATS")))
        if successful:
            self._subs.add(self.next_level.clicked.subscribe(lambda _: self.push_next_level(previous_screen+1, save_file)))
        else:
            self._subs.add(self.retry.clicked.subscribe(lambda _: self.push_next_level(previous_screen, save_file)))

        self.play_music()

    def push_next_level(self, next_screen, save_file):
        from controller.story_mode.level1_screen import Level1Screen
        from controller.story_mode.level2_screen import Level2Screen
        from controller.story_mode.level3_screen import Level3Screen
        from controller.story_mode.level4_screen import Level4Screen
        # from controller.story_mode.level5_screen import Level5Screen

        match next_screen:
            case 1:
                self.reload_screen(Level1Screen.init_fn(save_file))
            case 2:
                self.reload_screen(Level2Screen.init_fn(save_file))
            case 3:
                self.reload_screen(Level3Screen.init_fn(save_file))
            case 4:
                self.reload_screen(Level4Screen.init_fn(save_file))
            #case 5:
                #self.reload_screen(Level5Screen.init_fn(save_file))

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch

    def play_music(self):
        with contextlib.suppress(pygame.error):
            mixer.init()
            mixer.music.load("assets/sounds/Good Night.mp3")
            mixer.music.play(-1)