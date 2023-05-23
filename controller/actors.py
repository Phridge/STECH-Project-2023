from collections import namedtuple
from enum import Enum

import pyglet
from pyglet.image import Animation
from pyglet.sprite import Sprite
from reactivex import Observable
from reactivex.disposable import CompositeDisposable
from reactivex.operators import scan, distinct_until_changed, map as rmap, combine_latest

import ui_elements
import time
import color_scheme
from events import Disposable, Var, Event
from ui_elements import Gif
from ui_elements_ex import Rect


class Player:
    def __init__(self, events, batch, fx, fy, fwidth, fheight):
        self.x = fx
        self.y = fy
        self.own_width = fwidth
        self.own_height = fheight
        self.batch = batch
        self.events = events

        self.gif = ui_elements.GifButton("assets/images/mech_idle.gif", self.x, self.y, self.own_width, self.own_height, 0.75, True, self.events, self.batch)
        self.subs = CompositeDisposable()

    def idle(self):
        self.gif = ui_elements.Gif("assets/images/mech_idle.gif", self.x, self.y, self.own_width, self.own_height, 0.75, True, self.events, self.batch)

    def walk(self):
        self.gif = ui_elements.Gif("assets/images/mech_walk.gif", self.x, self.y, self.own_width, self.own_height, 0.75, True, self.events, self.batch)

    def jump(self, data):
        # von Janek übernommen, funktioniert hier noch nicht, wollte mir den schnipsel nur aufheben
        if data:
            self.gif.delete()
            self.gif = ui_elements.GifButton("assets/images/mech_jump.gif", self.x, self.y, self.own_width, self.own_height, 1, True, self.events, self.batch)
            self.subs = self.gif.loop_finished.subscribe(lambda _: self.hurt(False))
        else:
            self.gif.delete()
            self.gif = ui_elements.GifButton("assets/images/mech_walk.gif", self.x, self.y, self.own_width, self.own_height, 0.75, True, self.events, self.batch)
            if self.subs:
                self.subs.dispose()

    def hurt(self, data):
        # von Janek übernommen, funktioniert hier noch nicht, wollte mir den schnipsel nur aufheben
        if data:
            self.gif.delete()
            self.gif = ui_elements.GifButton("assets/images/mech_hurt.gif", 30, 12, 13, 20, 0.25, True, self.events,
                                             self.batch)
            self.subs = self.gif.loop_finished.subscribe(lambda _: self.hurt(False))
        else:
            self.gif.delete()
            self.gif = ui_elements.GifButton("assets/images/mech_walk.gif", 30, 12, 13, 20, 0.75, True, self.events,
                                             self.batch)
            if self.subs:
                self.subs.dispose()


    def die(self):
        self.gif = ui_elements.Gif("assets/images/mech_hurt.gif", 20, 40, 20, 30, 0.75, True, self.events, self.batch)
        time.sleep(1)
        self.idle()


class ThePlayer(Disposable):
    def __init__(self, pos=Rect(0, 0, 0, 0), look_dir=1, running_speed=0.0, batch=None, group=None):
        self.pos = Var(pos) if pos is not None else Event()
        self.look_dir = Var(look_dir)
        self.running_speed = Var(running_speed)

        self._subs = CompositeDisposable()

        def create_sprite(speed):
            if speed > 0:
                path = "assets/images/mech_walk.gif"
                anim = pyglet.image.load_animation(path)
                for frame in anim.frames:
                    frame.duration = (1 / speed) / len(anim.frames)
            else:
                path = "assets/images/mech_idle.gif"
                anim = pyglet.image.load_animation(path)

            return Sprite(anim, 0, 0, 0, batch=batch, group=group)

        sprite = self.running_speed.pipe(
            distinct_until_changed(),
            rmap(create_sprite)
        )

        def update_sprite_transform(data):
            sprite, look_dir, pos = data
            sprite.position = pos.x, pos.y, 0
            if pos.w * pos.h > 0:
                sprite.scale_x = pos.w * sprite.scale_x / sprite.width
                sprite.scale_y = pos.h * sprite.scale_y / sprite.height
            return sprite

        self._subs.add(
            sprite.pipe(
                combine_latest(self.look_dir, self.pos),
            ).subscribe(update_sprite_transform)
        )

    def move(self, dx, dy):
        curr_pos = self.pos.value
        self.pos.on_next(Rect(curr_pos.x + dx, curr_pos.y + dy, curr_pos.w, curr_pos))




class Enemy():
    def __init__(self, events, batch, fx, fy, fwidth, fheight):
        self.x = fx
        self.y = fy
        self.own_width = fwidth
        self.own_height = fheight
        self.batch = batch
        self.events = events

        self.gif = ui_elements.Gif("assets/images/enemy_walk_flipped.gif", self.x, self.y, self.own_width,
                                   self.own_height, 0.75, True, self.events, self.batch)

        self.header = ui_elements.BorderedRectangle("Type me", 20, 80, 60, 20, self.events.color_scheme,
                                                    color_scheme.Minecraft, 2, self.events, self.batch)