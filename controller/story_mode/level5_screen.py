import logging
import time

import contextlib
import pyglet
import pygame
import color_scheme
import ui_elements
from pygame import mixer
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable
from controller import Screen

"""
Noch nicht implementiert
"""

class Level5Screen(Screen):
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

        self.gif = ui_elements.Gif("assets/images/bridge.gif", 0, 0, 100, 100, 4, True, self.events, self.batch, background)

        self.header = ui_elements.BorderedRectangle("Level 5: Die Teestube <<Ruhe und Genuss>>' ", 20, 80, 60, 20, self.events.color_scheme, color_scheme.Minecraft, 2, self.events, self.batch)

        # Hier muss für jeden Button eine Subscription erstellt werden.

        self.change_controller = Subject()
        self.event = Subject()  # separates Subject für eventuelle Events die in diesem Screen stattfinden
    #  Falls die Funktionen namentlich nicht passen erstellte einfach neue!

    def button_clicked(self, data):  # Wird getriggert, wenn ein Spielstand ausgewählt wird
        self.change_controller.on_next(("HomeScreen", data))

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch


