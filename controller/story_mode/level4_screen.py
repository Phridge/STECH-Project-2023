import logging
import time

import pyglet
import pygame
from pygame import mixer
import contextlib

import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable
from controller import Screen

"""
Level4 noch nicht implementiert, Inhalt auch veraltet
"""

class Level4Screen(Screen):
    def __init__(self, events):
        super().__init__()
        self.events = events
        self.batch = pyglet.graphics.Batch()
        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        background = pyglet.graphics.Group(order=-1)
        foreground = pyglet.graphics.Group(order=1)

        # Liste, die sämtliche subscriptions fängt, um sie beim Wechseln des Controllers wieder freizugeben
        # self.sublist = []

        self.gif = ui_elements.Gif("assets/images/city.gif", 0, 0, 100, 100, 5, True, self.events, self.batch, background)
        self.header = ui_elements.BorderedRectangle("Level 4: Die Dampfstadt", 20, 80, 60, 20, self.events.color_scheme, color_scheme.Minecraft, 2, self.events, self.batch)


        # Hier muss für jeden Button eine Subscription erstellt werden.


        self.change_controller = Subject()


    def button_clicked(self, data):  # Wird getriggert, wenn ein Spielstand ausgewählt wird
        self.change_controller.on_next(("HomeScreen", data))

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
    def play_music(self):
        with contextlib.suppress(pygame.error):
            mixer.init()
            mixer.music.load("assets/sounds/MEGALOVANIA.mp3")
            mixer.music.play(-1)
