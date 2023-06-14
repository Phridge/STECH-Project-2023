from functools import lru_cache
from typing import Callable, Any, Generator

import pyglet
import pyglet.resource
import pyglet.image
from pyglet.graphics import Group
from reactivex import Observable
from reactivex.abc import DisposableBase
from reactivex.disposable import SerialDisposable, CompositeDisposable, Disposable
from reactivex.operators import scan, take_while, map as rmap

import color_scheme
import ui_elements
from controller import Screen
from ui_elements_ex import map_inner_perc
from events import Var, Event


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
    def __init__(self, events, save):
        super().__init__()

        # zugehöriger save dieses levels.
        self.save = save
        # ob pausiert ist.
        self.is_paused = Var(False)
        # events für das level an sich, kann ausgeschaltet werden. (per is_paused)
        self.events = events.add_valve(self.is_paused.pipe(rmap(lambda p: not p)))
        # events für das is_paused menü, funktioniert immer.
        self.pause_events = events

        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        self.background = Group(0)
        self.foreground = Group(1)
        self.hud = Group(2)
        self.overlay = Group(3)
        self.pause_background = Group(4)
        self.pause_foreground = Group(5)

        # pausier-button
        self.pause_visible = ui_elements.BorderedRectangleButton("Pause (Esc)", 2.5, 85, 15, 10,
                                                                 self.events.color_scheme, color_scheme.Minecraft, 6,
                                                                 self.events, self.batch, self.foreground)
        # wird escape gedruckt?
        self._subs.add(self.events.key.subscribe(self.test_for_escape))
        # pausieren, wenn click
        self._subs.add(self.pause_visible.clicked.subscribe(lambda _: self.pause()))

        # disposable objekte für den is_paused screen.
        self.pause_sub = SerialDisposable()
        self._subs.add(self.is_paused.subscribe(self._show_pause))

    def test_for_escape(self, data):
        if data[0] == 65307:
            self.pause()

    def pause(self):
        """Pausiere. (zeige pausescreen an)"""
        self.is_paused.on_next(True)

    def unpause(self):
        """zurück zum Spiel (pausescreen weg)"""
        self.is_paused.on_next(False)

    def _show_pause(self, show):
        """
        Blendet über dem aktuellen Level einen komplett neuen Bildschirm ein, pausiert im Hintergrund die Funktionen des Levels

        :param show: ob das is_paused menü angezeigt werden soll. angezeigt werden soll.
        """
        if not show:
            self.pause_sub.disposable = None
            return

        from controller.story_mode.main_screen import MainStoryScreen

        # Erstes Layout für den HomeScreen
        pause_back = ui_elements.InputButton("Level verlassen", 15, 5, 15, 7.5, self.pause_events.color_scheme, color_scheme.Minecraft, 7, self.pause_events, self.batch, self.pause_foreground)
        pause_continue_level = ui_elements.InputButton("Fortsetzen", 40, 5, 20, 10, self.pause_events.color_scheme, color_scheme.Minecraft, 8.4, self.pause_events, self.batch, self.pause_foreground)
        pause_background = ui_elements.Sprite("assets/images/tearoom.png", 0, 0, 100, 100, self.pause_events, self.batch, self.pause_background)
        pause_maxwell = ui_elements.Sprite("assets/images/mech_tea.png", 40, 17.5, 20, 37.5, self.pause_events, self.batch, self.pause_foreground)
        pause_header = ui_elements.BorderedRectangle("Tee-Pause", 20, 75, 60, 20, self.pause_events.color_scheme, color_scheme.Minecraft, 5, self.pause_events, self.batch, self.pause_foreground)

        # hier alle disposable resourcen
        self.pause_sub.disposable = CompositeDisposable(
            pause_back.clicked.subscribe(lambda _: self.reload_screen(MainStoryScreen.init_fn(self.save))),
            pause_continue_level.clicked.subscribe(lambda _: self.unpause()),
            pause_back,
            pause_continue_level,
            pause_background,
            pause_maxwell,
            pause_header,
        )


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



# folgende Funktionen sind zum Laden bestimmter Animationen für Spielobjekte.
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