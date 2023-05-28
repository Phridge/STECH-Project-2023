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
from controller.actors import Player
from controller.actors import Enemy

"""
Eine Vorlage für einen Screen. ab Zeile 22 können Elemente eingefügt werde. Ein paar der ui-Elements sind als Beispiel gezeigt.
In dieser Datei sind nur die absoluten Essentials drin. Hinzufügen ist kein Problem, löschen schon.
Lasst euch dieses Template anzeigen, indem ihr es im main_controller als initialen Controller setzt :D
"""

class Level2Screen(Screen):
    def __init__(self, events):
        super().__init__()
        self.events = events
        self.batch = pyglet.graphics.Batch()
        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        background = pyglet.graphics.Group(order=-1)
        foreground = pyglet.graphics.Group(order=1)

        # im folgenden Block können Elemente eingefügt werden. Die Elemente die schon da sind dienen nur als Beispiele
        self.gif = ui_elements.Gif("assets/images/forest.gif", 0, 0, 100, 100, 30, True, self.events, self.batch, background)

        # Player-Objekt
        player = Player(self.events, self.batch, 40, 12, 20, 30)

        # Test Enemy-Objekt
        enemy = Enemy(self.events, self.batch, 70, 12, 7.5, 15)

        self.header = ui_elements.BorderedRectangle("Level 2: Der Wald des Widerstands", 20, 80, 60, 20, self.events.color_scheme, color_scheme.Minecraft, 2, self.events, self.batch)

        # Hier muss für jeden Button eine Subscription erstellt werden.
        # In der Lambda-Funktion wird dann die Funktion angebgeben, die aufgerufen werden soll wenn der jeweilige Button gedrückt wird
        # self._subs.add(self.mech.clicked.subscribe(lambda _: self.mech_hurt(True)))
        # self.mech_sub = None

    #  Falls die Funktionen namentlich nicht passen erstellte einfach neue!

    def mech_hurt(self, data):
        if data:
            logging.warning("AUA")
            self.mech.delete()
            self.mech = ui_elements.GifButton("assets/images/mech_hurt.gif", 30, 12, 13, 20, 0.25, True, self.events, self.batch)
            self.mech_sub = self.mech.loop_finished.subscribe(lambda _: self.mech_hurt(False))
        else:
            self.mech.delete()
            self.mech = ui_elements.GifButton("assets/images/mech_walk.gif", 30, 12, 13, 20, 0.75, True, self.events, self.batch)
            if self.mech_sub:
                self.mech_sub.dispose()

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch

    def play_music(self, nextmusic):
        with contextlib.suppress(pygame.error):
            mixer.init()
            mixer.music.load(nextmusic)
            mixer.music.play()
            mixer.music.play(-1)