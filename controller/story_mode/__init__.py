from functools import lru_cache
from typing import Callable, Any, Generator

import pyglet
import pyglet.resource
import pyglet.image
from pyglet.graphics import Group
from reactivex import Observable
from reactivex.abc import DisposableBase
from reactivex.disposable import SerialDisposable
from reactivex.operators import scan, take_while, map as rmap

from controller import Screen


class Machine(DisposableBase):
    """
    Stellt den Ablauf des Levels in einer Finite State Machine dar.
    Hat mehrere Schritte, die nacheinander abgearbeitet werden (durch machine.next()).
    """

    def __init__(self, stuff):
        self.stuff = stuff
        self.index = -1
        self.disposable = SerialDisposable()
        self.next()

    def next(self):
        """
        Die Maschine in den nächsten Zustand bringen

        Die Ressourcen vom vorherigen Schritt, falls existierend, werden gelöscht, und die
        Funktion des nächsten Zustands wird ausgeführt.
        """
        self.index += 1
        if self.index >= len(self.stuff):
            return
        self.disposable.disposable = self.stuff[self.index]()

    def dispose(self):
        self.disposable.dispose()


class LevelMachine(DisposableBase):
    """
    Eine State Machine für Level, welche über python-Generator-Funktionen implementiert ist.

    Für Beispiel s. Level2 Screen.
    """
    def __init__(self, generator_func: Callable[[Any], Generator]):
        """
        Initialisiere eine LevelMachine.

        :param generator_func: eine Funktion, die einen Generator kreiert (also eine funktion, die yield statements
        enthält) und EIN Argument annimmt. Dieses eine Argument wird eine Funktion sein, die aus dem Generator aufgerufen
        werden kann, um ausführung des Generators fortzufahren.
        """
        self.machine_disposable = SerialDisposable()

        self.generator = generator_func(self.switch_state)

        self.switch_state(None)

    def switch_state(self, data=None):
        """
        Gehe in den nächsten Zustand über.
        :param data: Daten, die an den Generator gesendet werden.
        :return: nichts
        """
        self.machine_disposable.disposable = None
        try:
            self.machine_disposable.disposable = self.generator.send(data)
        except StopIteration:
            pass

    def dispose(self) -> None:
        self.machine_disposable.dispose()


class Level(Screen):
    """
    Superklasse für Storylevel.

    Stellt bereit:
    * mehrere gruppen zum reinrendern, gerne auch untergruppen für diese erstellen wenn nötig
    """
    def __init__(self):
        super().__init__()


        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        self.background = Group(0)
        self.foreground = Group(1)
        self.overlay = Group(2)

    def pause(self):
        pass


def linear(t):
    return t


def animate(lo, hi, time, update_event, map=lambda x: x, interp=linear) -> Observable:
    """
    Animiert einen Wert von lo nach hi über gegebene Zeit.
    :param lo: startwert.
    :param hi: endwert.
    :param time: zeitspanne der animation.
    :param update_event: observable, welches das "timing" vorgibt (z.B. events.update)
    :param map: optionale mapping-funktion, die den Animierten wert in etwas anderes konvertiert.
    :param interp: Interpolierungsfunktion. zur verfügung steht aktuell "linear", welches gleichmäßig vom einen zum anderen wert animiert.
    :return: Ein Observable, welches schrittweise den animierten wert liefert
    """
    animation = update_event.pipe(
        scan(float.__add__, 0.0),
        take_while(lambda t: t <= time, inclusive=True),
        rmap(lambda t: lo + (hi - lo) * interp(min(t, time) / time)),
        rmap(map)
    )
    return animation


@lru_cache()
def load_enemy_idle(duration=0.3):
    sprite_sheet = pyglet.resource.image('assets/images/enemy_idle.png')
    image_grid = pyglet.image.ImageGrid(sprite_sheet, rows=1, columns=4)
    return pyglet.image.Animation.from_image_sequence(image_grid, duration)


@lru_cache()
def load_enemy_barrel_run(duration=0.1):
    sprite_sheet = pyglet.resource.image('assets/images/enemy_barrel_run.png')
    image_grid = pyglet.image.ImageGrid(sprite_sheet, rows=1, columns=4)
    return pyglet.image.Animation.from_image_sequence(image_grid, duration)


@lru_cache()
def load_enemy_run():
    return pyglet.image.load_animation("assets/images/enemy_run.gif")


@lru_cache()
def load_bush():
    return pyglet.image.load("assets/images/bush.png")