import pyglet
from reactivex.disposable import CompositeDisposable

import ui_elements
import time
import color_scheme
from ui_elements import Gif


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