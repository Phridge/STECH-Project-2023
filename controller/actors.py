from collections import namedtuple

import pyglet
import reactivex
from pyglet.math import Vec2
from pyglet.sprite import Sprite
from reactivex import Observable
from reactivex.disposable import CompositeDisposable
from reactivex.operators import scan, distinct_until_changed, combine_latest, starmap, share

import ui_elements
import time
import color_scheme
from events import Disposable, Var, Unset, OptVar
from ui_elements_ex import Rect, rx


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


def combine_offset(offset: Observable):
    """
    Pipe-Operator, um einen Rect-Observable-Stream um
    die positionsangaben eines anderen Rect-Observable-Streams zu offsetten.
    :param offset: Rect-Observable-Stream, der das offset angibt
    :return: einen Operator für observable.pipe, der eben gesagtes tut
    """
    return reactivex.compose(
        combine_latest(offset),
        starmap(Rect.offset)
    )


def continuous_sum(initial=0):
    """
    Pipe-Operator, um werte in einem Stream zu summieren.
    :param initial: initialwert
    :return: ein Operator für observable.pipe
    """
    return scan(lambda acc, new: acc + new, initial)



class ThePlayer(Disposable):
    """
    Spieler-Klasse auf reactivex-Basis.

    Hat Grundlegend eine Positionierung (pos) in form eines Rect(x, y, w, h) (enthält größe!), eine richtung, in die geguckt
    wird, und einen Status. Dieser bestimmt über die Animation. Idle: steht da. Running: Rennen mit geschwindigkeit.
    Jumping: nocht nicht drin, sollte evtl. Springanimation oder so machen. GERNE WEITERS HINZUFÜGEN
    """

    Idle = namedtuple("Idle", "")
    Running = namedtuple("Running", "speed")
    Jumping = namedtuple("Jumping", "")

    def __init__(self, pos=Rect.zero(), look_dir=1, state=Idle(), batch=None, group=None):
        """
        Initialisiere den Spieler.

        pos, look_dir, und state nehmen auch Observables an. Die Übergebenen Werte werden 1:1 im Objekt gespeichert,
        somit können, sofern Var() oder Event() übergeben wurden, diese Observable noch per spieler.state.on_next(x)
        aufgerufen werden (s. Level 1)

        :param pos: Position und Größe des spielers. Rect() oder Observable mit Rect()
        :param look_dir: Blickrichtung. 1 für rechts, -1 für links
        :param state: Idle(), Running(speed), Jumping() usw.
        :param batch: Zeichen-Batch
        :param group: Gruppe
        """
        self.pos = rx(pos)  # rx() wrappt nicht-Observable-Argumente und macht welche draus, wenn dies nicht sind
        self.look_dir = rx(look_dir)
        self.state = rx(state)

        def create_sprite(old_sprite: pyglet.sprite.Sprite | None, state):
            """
            Mapper-Funktion, die auf Zustandsänderungen (Änderungen in state) und entsprechend old_sprite anpasst.
            :param old_sprite: die vorherige Sprite (beim ersten mal None)
            :param state: der neue Zustand
            :return: aktualisierte Sprite. Es ändert sich nur die Animation.
            """
            match state:
                case self.Idle():
                    path = "assets/images/mech_idle.gif"
                    anim = pyglet.image.load_animation(path)
                case self.Running(speed):
                    path = "assets/images/mech_walk.gif"
                    anim = pyglet.image.load_animation(path)
                    for frame in anim.frames:
                        frame.duration = (1 / speed) / len(anim.frames)
                case _:
                    raise NotImplementedError

            if old_sprite is None:
                sprite = Sprite(anim, 0, 0, 0, batch=batch, group=group)
                sprite.visible = False
            else:
                sprite = old_sprite
                sprite.image = anim

            return sprite


        def update_sprite_transform(sprite, look_dir, pos):
            """
            Reagiert auf richtungs- und Größenänderungen und passt die Sprite entsprechend an.
            :param sprite: aktuelle sprite
            :param look_dir: blickrichtung
            :param pos: position
            :return: aktualisierte sprite
            """
            sprite.position = pos.x, pos.y, 0

            if look_dir < 0:  # falls look_dir -1 ist
                sprite.x += pos.w

            if pos.w * pos.h > 0:
                sprite.scale_x = pos.w * sprite.scale_x / sprite.width
                if look_dir * sprite.scale_x <= 0:  # falls look_dir -1 ist
                    sprite.scale_x *= -1
                sprite.scale_y = pos.h * sprite.scale_y / sprite.height

                # sichtbar machen, wenns nicht schon geschehen ist
                if not sprite.visible:
                    sprite.visible = True

            return sprite

        sprite = self.state.pipe(
            scan(create_sprite, None),
            combine_latest(self.look_dir, self.pos),
            starmap(update_sprite_transform),
        )

        self._sub = sprite.subscribe()  # muss gemacht werden, damit auch was passiert (lol)



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