import itertools
import logging
import time
from functools import partial

import pyglet
import pygame
from pygame import mixer
import contextlib

from pyglet.graphics import Group
from pyglet.resource import animation
from reactivex import Observable, just, interval
from reactivex.operators import combine_latest, map as rmap, share, starmap, multicast, scan

import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable

from controller import Screen
from controller.actors import Player, Enemy, ThePlayer, combine_offset, StaticActor, continuous_sum
from ui_elements_ex import rx, Rect, Style, map_inner_perc
from events import Event, Var
from . import Level, Machine, animate

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
        window = events.size.pipe(
            rmap(lambda s: Rect(0, 0, *s))
        )
        style = Style(events.color_scheme, "Monocraft", 15)
        player_group = Group(0, parent=self.foreground)
        bush_group = Group(1, parent=self.foreground)
        enemy_group = Group(2, parent=self.foreground)
        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund

        # im folgenden Block können Elemente eingefügt werden. Die Elemente die schon da sind dienen nur als Beispiele
        self.gif = ui_elements.Gif("assets/images/forest.gif", 0, 0, 100, 100, 30, True, self.events, self.batch, self.background)


        def generate_bush_enemy_positions():
            curr = 0
            inc = 500
            iinc = 1.01
            while True:
                yield Rect(curr, -30, 150, 100), Rect(curr + inc / 2, -10, 100, 130)
                curr += inc
                inc *= iinc


        positions = list(itertools.islice(generate_bush_enemy_positions(), 1000))

        level_progress = Var(0)

        sprite_sheet = pyglet.resource.image('assets/images/enemy_idle.png')
        image_grid = pyglet.image.ImageGrid(sprite_sheet, rows=1, columns=4)
        enemy_animation = pyglet.image.Animation.from_image_sequence(image_grid, duration=0.3); del sprite_sheet, image_grid
        bush_animation = pyglet.image.load("assets/images/bush.png")

        object_area = window.pipe(
            map_inner_perc(0, 10, 100, 90)
        )

        scroll = Var(0)
        scroll_off = scroll.pipe(
            rmap(lambda o: Rect(-o, 0, 0, 0))
        )

        # Player-Objekt

        player_stationary = Rect(100, -10, 130, 130)
        player_pos = Var(player_stationary)
        self.player = ThePlayer(
            pos=player_pos.pipe(combine_offset(object_area)),
            state=Var(ThePlayer.Running(4.0)),
            batch=self.batch,
            group=player_group,
        )


        level_enemies = []

        def generate_enemies(index):
            bush_pos, enemy_pos = positions[index]

            enemy = StaticActor(
                enemy_animation,
                just(enemy_pos).pipe(
                    combine_offset(scroll_off),
                    combine_offset(object_area)
                ),
                look_dir=-1,
                batch=self.batch,
                group=enemy_group
            )


            bush = StaticActor(
                bush_animation,
                just(bush_pos).pipe(
                    combine_offset(scroll_off),
                    combine_offset(object_area),
                ),
                batch=self.batch,
                group=bush_group
            )

            return bush, enemy

        generate_ahead = 5

        for i in range(generate_ahead):
            level_enemies.append(generate_enemies(i))


        def rotate_enemies(index):
            level_enemies.pop(0)
            level_enemies.append(generate_enemies(index + generate_ahead))

        self._subs.add(level_progress.subscribe(rotate_enemies))


        def scroll_to_progress(index):
            if index == 0:
                lo = -1500
                time = 4
            else:
                lo = positions[index-1][0].x - 100
                time = 1
            hi = positions[index][0].x - 100

            disposable = animate(lo, hi, time, events.update).subscribe(scroll.on_next, on_completed=lambda: disposable.dispose())


        self._subs.add(level_progress.subscribe(scroll_to_progress))

        self.events.text.subscribe(lambda _: level_progress.on_next(level_progress.value + 1))

        def player_enter():

            return CompositeDisposable([

            ])

        machine = Machine([
            player_enter,
        ])




        self.header = ui_elements.BorderedRectangle("Level 2: Der Wald des Widerstands", 20, 80, 60, 20, self.events.color_scheme, color_scheme.Minecraft, 2, self.events, self.batch, self.foreground)

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