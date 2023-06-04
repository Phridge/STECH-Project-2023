from functools import lru_cache
from typing import Callable, Any, Generator

import pyglet
import pyglet.resource
import pyglet.image
from pyglet.graphics import Group
from reactivex import Observable
from reactivex.abc import DisposableBase
from reactivex.disposable import SerialDisposable, CompositeDisposable
from reactivex.operators import scan, take_while, map as rmap

import color_scheme
import ui_elements
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


    def pause(self, events, save):
        from controller.story_mode.main_screen import MainStoryScreen
        background = pyglet.graphics.Group(order=2)
        middleground = pyglet.graphics.Group(order=3)

        # Erstes Layout für den HomeScreen
        pause_back = ui_elements.InputButton("Level verlassen", 15, 5, 15, 7.5, events.color_scheme, color_scheme.Minecraft, 7, events, self.batch, middleground)
        pause_continue_level = ui_elements.InputButton("Fortsetzen", 40, 5, 20, 10, events.color_scheme, color_scheme.Minecraft, 8.4, events, self.batch, middleground)
        pause_background = ui_elements.Sprite("assets/images/tearoom.png", 0, 0, 100, 100, events, self.batch, background)
        pause_maxwell = ui_elements.Sprite("assets/images/mech_tea.png", 40, 17.5, 20, 37.5, events, self.batch, middleground)

        pause_header = ui_elements.BorderedRectangle("Tee-Pause", 20, 75, 60, 20, events.color_scheme, color_scheme.Minecraft, 5, events, self.batch, middleground)

        pause_subs = CompositeDisposable()
        pause_subs.add(pause_back.clicked.subscribe(lambda _: self.reload_screen(MainStoryScreen.init_fn(save))))
        pause_subs.add(pause_continue_level.clicked.subscribe(lambda _: self.unpause(pause_header, pause_maxwell, pause_background, pause_subs, pause_back, pause_continue_level)))

    def unpause(self, pause_header, pause_maxwell, pause_background, pause_subs, pause_back, pause_continue_level):
        print("subs")
        pause_subs.dispose()
        print("back")
        pause_back.stop_timer()
        pause_back.dispose()

        print("continue")
        pause_continue_level.stop_timer()
        pause_continue_level.dispose()
        print("BG")
        pause_background.delete()
        print("maxwell")
        pause_maxwell.delete()
        print("header")
        pause_header.delete()


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