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
from tools import save_and_open


class UserDocumentationScreen(Screen):
    def __init__(self, events):
        super().__init__()
        self.batch = pyglet.graphics.Batch()
        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        # einfach foreground oder background als zusätzliche Variable ans Element packen
        background = pyglet.graphics.Group(order=-1)
        foreground = pyglet.graphics.Group(order=1)

        # Erstes Layout für den Hauptbildschirm
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, self.batch)
        self.header = ui_elements.BorderedRectangle("So funktioniert alles:", 20, 75, 60, 20, events.color_scheme, color_scheme.Minecraft, 3.5, events, self.batch)
        self.maneuvering = ui_elements.BorderedRectangle("Manövrierung:", 30, 62.5, 40, 10, events.color_scheme, color_scheme.Minecraft, 6, events, self.batch)
        self.maneuvering_text = ui_elements.BorderedRectangle("Du brauchst keine Maus, alle Buttons die blinken kannst du über die Tastatur eingeben!", 5, 53.375, 90, 7.5, events.color_scheme, color_scheme.Minecraft, 1.3, events, self.batch)
        self.settings = ui_elements.BorderedRectangle("Einstellungen:", 30, 42.5, 40, 10, events.color_scheme, color_scheme.Minecraft, 6, events, self.batch)
        self.settings_text = ui_elements.BorderedRectangle("In den Einstellungen kannst du mit \"Tab\" und \"Shift+Tab\" manövrieren", 5, 33.375, 90, 7.5, events.color_scheme, color_scheme.Minecraft, 1.7, events, self.batch)
        self.settings = ui_elements.BorderedRectangle("10-Finger-Schreiben:", 30, 22.5, 40, 10, events.color_scheme, color_scheme.Minecraft, 5, events, self.batch)
        self.settings_text = ui_elements.BorderedRectangle("Versuche beim Tippen nicht auf die Tastatur zu schauen!", 5, 12.375, 90, 7.5, events.color_scheme, color_scheme.Minecraft, 2, events, self.batch)

        self.back = ui_elements.InputButton("Zurück", 40, 2.5, 20, 7.5, events.color_scheme, color_scheme.Minecraft, 8, events, self.batch)


        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        self._subs.add(self.back.clicked.subscribe(lambda _: self.go_back()))

        self.play_music(events.volume)

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch


    def play_music(self, volume): #Musik im Start Menü
        with contextlib.suppress(pygame.error):
            mixer.music.load("assets/sounds/02 Start Menu.mp3")
            mixer.music.play()
            mixer.music.play(-1)
