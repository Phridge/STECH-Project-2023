import random
from collections import namedtuple

import pyglet
import reactivex
from pyglet.math import Vec2
from pyglet.sprite import Sprite
from reactivex import Observable
from reactivex.disposable import CompositeDisposable
from reactivex.operators import scan, distinct_until_changed, combine_latest, starmap, share, map as rmap

import ui_elements
import time
import color_scheme
from events import Disposable, Var, Unset, OptVar
from ui_elements_ex import Rect, rx

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


class Actor(Disposable):
    """
    Abstrakte klasse, um Spieler und andere Objekte zu abstrahieren.

    Kann in Unterklassen um weitere Zustände erweitert werden.
    """

    Idle = namedtuple("Idle", "")

    def __init__(self, pos=None, look_dir=None, state=None, batch=None, group=None):
        """
        Initialisiere den Actor.

        pos, look_dir, und state nehmen auch Observables an. Die Übergebenen Werte werden 1:1 im Objekt gespeichert,
        somit können, sofern Var() oder Event() übergeben wurden, diese Observable noch per spieler.state.on_next(x)
        aufgerufen werden (s. Level 1)

        :param pos: Position und Größe des Actors. Rect() oder Observable mit Rect()
        :param look_dir: Blickrichtung. 1 für rechts, -1 für links
        :param state: Idle(), Running(speed), Jumping() usw.
        :param batch: Zeichen-Batch
        :param group: Gruppe
        """
        self.pos = rx(pos, Rect.zero())  # rx() wrappt nicht-Observable-Argumente und macht welche draus, wenn dies nicht sind
        self.look_dir = rx(look_dir, 1)
        self.state = rx(state, self.Idle())
        self.batch = batch
        self.group = group


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
            rmap(self._get_image),
            scan(self.create_sprite, None),
            combine_latest(self.look_dir, self.pos),
            starmap(update_sprite_transform),
        )

        self._sub = sprite.subscribe(lambda s: setattr(self, "sprite", s))  # muss gemacht werden, damit auch was passiert (lol)
        self._on_dispose = reactivex.disposable.Disposable(lambda: self.sprite.delete())

    def create_sprite(self, old_sprite: pyglet.sprite.Sprite | None, image):
        """
        Mapper-Funktion, die auf Änderungen des anzuzeigenden Bildes reagiert und ein Sprite-Objekt anpasst.
        :param old_sprite: die vorherige Sprite (beim ersten mal None)
        :param image: neues bild, geladen durch _get_image(self)
        :return: aktualisierte Sprite. Es ändert sich nur die Animation.
        """
        if old_sprite is None:
            sprite = Sprite(image, 0, 0, 0, batch=self.batch, group=self.group)
            sprite.visible = False
        else:
            sprite = old_sprite
            sprite.image = image

        return sprite

    def _get_image(self, state):
        """
        Erstellt das anzuzeigende Bild für gegebenen Zustand.

        Muss überschrieben werden durch unterklassen.
        :param state: aktueller Zustand
        :return: ein Bild entsprechend des Zustands
        """
        raise NotImplementedError


class ThePlayer(Actor):
    """
    Spieler-Klasse auf reactivex-Basis.

    Hat Grundlegend eine Positionierung (pos) in form eines Rect(x, y, w, h) (enthält größe!), eine richtung, in die geguckt
    wird, und einen Status. Dieser bestimmt über die Animation. Idle: steht da. Running: Rennen mit geschwindigkeit.
    Jumping: nocht nicht drin, sollte evtl. Springanimation oder so machen. GERNE WEITERS HINZUFÜGEN
    """

    Running = namedtuple("Running", "speed")
    Jumping = namedtuple("Jumping", "")
    Hurt = namedtuple("Hurt", "")
    Attacking = namedtuple("Attacking", "attack")

    def __init__(self, pos=None, look_dir=None, state=None, batch=None, group=None):
        super().__init__(pos, look_dir, state, batch, group)

    def _get_image(self, state):
        match state:
            case self.Idle():
                path = "assets/images/mech_idle.gif"
                return pyglet.image.load_animation(path)
            case self.Running(speed):
                path = "assets/images/mech_walk.gif"
                anim = pyglet.image.load_animation(path)
                for frame in anim.frames:
                    frame.duration = (1 / speed) / len(anim.frames)
                return anim
            case self.Hurt():
                return pyglet.image.load_animation("assets/images/mech_hurt.gif")
            case self.Attacking(attack):
                if attack is None:
                    attack_id, frames, duration = random.choice([
                        (1, 4, 0.3),
                        (2, 6, 1),
                        (3, 4, 0.3),
                        (4, 6, 1)
                    ])
                    path = f"assets/images/mech_attack_{attack_id}.png"
                    sprite_sheet = pyglet.resource.image(path)
                    image_grid = pyglet.image.ImageGrid(sprite_sheet, rows=1, columns=frames)
                    return pyglet.image.Animation.from_image_sequence(image_grid, duration / frames)
            case _:
                raise NotImplementedError



class StaticActor(Actor):
    """
    Actor, der nur einen Zustand hat und diesen nicht wechselt.

    Z.B. für Busch und so.
    """
    def __init__(self, image, pos=None, look_dir=None, batch=None, group=None):
        """
        Initialisiere diesen StaticActor.

        Will eine Image/Animation haben, die immer angezeigt wird.
        :param image:
        :param pos:
        :param look_dir:
        :param batch:
        :param group:
        """
        self.image = image
        super().__init__(pos, look_dir, self.Idle(), batch, group)

    def _get_image(self, state):
        return self.image
