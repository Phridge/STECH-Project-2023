import logging
import time

import pyglet
import pygame
from pygame import mixer
import contextlib

from reactivex import Observable
from reactivex.operators import combine_latest, map as rmap, share, starmap, multicast, scan

import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable

from controller import Screen
from controller.actors import Player, Enemy, ThePlayer
from ui_elements_ex import rx, Rect, Style, map_inner_perc
from events import Event, Var
from . import Level

"""
Eine Vorlage für einen Screen. ab Zeile 22 können Elemente eingefügt werde. Ein paar der ui-Elements sind als Beispiel gezeigt.
In dieser Datei sind nur die absoluten Essentials drin. Hinzufügen ist kein Problem, löschen schon.
Lasst euch dieses Template anzeigen, indem ihr es im main_controller als initialen Controller setzt :D
"""


def game_object(image, pos, batch=None, group=None) -> Observable:
    image = rx(image)
    pos = rx(pos)

    def create_sprite(old_sprite: pyglet.sprite.Sprite | None, img):
        if old_sprite:
            old_sprite.delete()
        sprite = pyglet.sprite.Sprite(img, subpixel=True, batch=batch, group=group)
        return sprite

    def position_sprite(sprite, pos):
        sprite.position = pos.x, pos.y, 0
        if pos.w * pos.h > 0:
            sprite.scale_x = pos.w * sprite.scale_x / sprite.width
            sprite.scale_y = pos.h * sprite.scale_y / sprite.height

    sprite = image.pipe(
        scan(create_sprite, None),
        share(),
        combine_latest(pos),
        starmap(position_sprite)
    )

    return sprite


class Level2Screen(Level):
    def __init__(self, events):
        super().__init__()
        self.events = events
        pos = events.size.pipe(
            rmap(lambda s: Rect(0, 0, *s))
        )
        style = Style(events.color_scheme, "Monocraft", 15)
        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund

        # im folgenden Block können Elemente eingefügt werden. Die Elemente die schon da sind dienen nur als Beispiele
        self.gif = ui_elements.Gif("assets/images/forest.gif", 0, 0, 100, 100, 30, True, self.events, self.batch, self.background)


        # Test Enemy-Objekt
        enemy = Enemy(self.events, self.batch, 70, 12, 7.5, 15)

        object_area = pos.pipe(
            map_inner_perc(0, 10, 100, 90)
        )

        # Player-Objekt
        self.player = ThePlayer(
            batch=self.batch,
            group=self.foreground,
        )

        self._subs.add(object_area.pipe(
            rmap(lambda p: Rect(p.x, p.y, 150, 150))
        ).subscribe(self.player.pos))

        self.bush = game_object(
            pyglet.image.load("assets/images/bush.png"),
            object_area.pipe(
                rmap(lambda p: Rect(p.x, p.y, 200, 200))
            ),
            batch=self.batch,
            group=self.foreground
        ).subscribe()

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