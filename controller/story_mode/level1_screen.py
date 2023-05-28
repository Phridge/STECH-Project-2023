import math
import time
from collections import namedtuple
from enum import Enum
from typing import NewType

import pyglet
import pygame
from pygame import mixer
import contextlib
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex import just, concat
from reactivex.operators import delay, scan, map as rmap, combine_latest, do_action, starmap, filter as rfilter, \
    take_while, share
from reactivex.disposable import CompositeDisposable, SerialDisposable, Disposable
from controller import Screen
from controller.actors import Player, ThePlayer
from controller.inputbox import InputBox
from input_tracker import InputAnalysis
from tools.save_and_open import save_text_tracker, save_run
from ui_elements_ex import Rect, map_inner_perc, Style, Rectangle
from events import Var, Event

"""
Eine Vorlage für einen Screen. ab Zeile 22 können Elemente eingefügt werde. Ein paar der ui-Elements sind als Beispiel gezeigt.
In dieser Datei sind nur die absoluten Essentials drin. Hinzufügen ist kein Problem, löschen schon.
Lasst euch dieses Template anzeigen, indem ihr es im main_controller als initialen Controller setzt :D
"""


def linear(t):
    return t


def animate(lo, hi, time, update_event, map=lambda x: x, interp=linear):
    animation = update_event.pipe(
        scan(float.__add__, 0.0),
        take_while(lambda t: t <= time, inclusive=True),
        rmap(lambda t: lo + (hi - lo) * interp(min(t, time) / time)),
        rmap(map)
    )
    return animation


class Level1Screen(Screen):

    TEXTS = """\
Hallo! Ich bin Maxwell.

Schön, dass du dich entschieden hast, das 10-Finger-Schreiben zu lernen.

Je schneller du schreibst, desto mehr Punkte warten am Ende jeden Levels auf dich.

Doch zunächst muss ich erstmal meine Freunde, die vom Maschinenkönig in der Dampfstadt gefangen halten werden, befreien!

Die Reise wird lang und herausfordernd, hoffentlich habe ich genug Ersatz-Teetassen mit. Ohne mein Lebenselixier geht nichts!

*SSSSSSSsssssssssssssssssip*

...genug Tee, nun gehts los!\
""".split("\n\n")

    def __init__(self, events, save):
        super().__init__()
        self.events = events
        pos = events.size.pipe(
            rmap(lambda s: Rect(0, 0, *s))
        )
        style = Style(events.color_scheme, "Monocraft", 15)
        self.batch = pyglet.graphics.Batch()
        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        background = pyglet.graphics.Group(order=-1)
        foreground = pyglet.graphics.Group(order=1)
        overlay = pyglet.graphics.Group(order=2)

        self.gif = ui_elements.Gif("assets/images/port.gif", 0, 0, 100, 100, 30, True, self.events, self.batch, background)

        # Player-Objekt
        # player = Player(self.events, self.batch, 20, 40, 20, 30)


        self.p = ThePlayer(batch=self.batch, group=foreground)
        player_area = pos.pipe(
            map_inner_perc(0, 40, 100, 60)
        )

        text = Event()

        input_analysis = InputAnalysis()
        self.input_box = InputBox(text, pos.pipe(map_inner_perc(10, 5, 80, 20)), style, events, input_analysis, batch=self.batch, group=foreground)
        self._subs.add(
            self.input_box.text_tracker.pipe(
                rfilter(lambda tt: tt.is_finished)
            ).subscribe(lambda _: machine.next())
        )

        self.header = ui_elements.BorderedRectangle("Level 1: Der Hafen der Freiheit", 20, 80, 60, 20, self.events.color_scheme, color_scheme.Minecraft, 2, self.events, self.batch)

        class Machine:
            def __init__(self, stuff):
                self.stuff = stuff
                self.index = -1
                self.disposable = SerialDisposable()
                self.next()

            def next(self):
                self.index += 1
                if self.index >= len(self.stuff):
                    return
                self.disposable.disposable = self.stuff[self.index]()

        def display_text(display_text):
            return lambda: text.on_next(display_text)

        def player_entry():
            color = animate(255, 0, 3.0, events.update, lambda o: (0, 0, 0, int(o)))
            player_pos = animate(-300, 100, 5.0, events.update).pipe(
                do_action(on_completed=lambda: machine.next()),
                combine_latest(player_area),
                starmap(lambda xoff, area: Rect(xoff, 0, 150, 150).offset(area)),
            )
            overlay_rect = Rectangle(pos, color, self.batch, overlay)

            self.p.running_speed.on_next(2.0)
            return CompositeDisposable(
                overlay_rect,
                player_pos.subscribe(self.p.pos),
                Disposable(lambda: self.p.running_speed.on_next(0.0))
            )

        def player_exit():
            # save game
            save_run(save, "story_level_1", input_analysis)

            color = animate(0, 255, 3.0, events.update, lambda o: (0, 0, 0, int(o))).pipe(delay(3.0))
            player_pos = animate(100, 2000, 10.0, events.update).pipe(
                do_action(on_completed=lambda: machine.next()),
                combine_latest(player_area),
                starmap(lambda xoff, area: Rect(xoff, 0, 150, 150).offset(area)),
            )

            overlay_rect = Rectangle(pos, color, self.batch, overlay)

            self.p.running_speed.on_next(4.0)
            return CompositeDisposable(
                overlay_rect,
                player_pos.subscribe(self.p.pos),
            )

        machine = Machine(
            [player_entry]
            + [display_text(text) for text in self.TEXTS]
            + [player_exit]
        )

        interactions = Event()
        self._subs.add(interactions.subscribe(lambda _: machine.next()))

        # self.test = pyglet.shapes.Arc(100, 100, 50, angle=math.pi, closed=True, batch=self.batch, group=foreground)


    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch

    def play_music(self, nextmusic):
        with contextlib.suppress(pygame.error):
            mixer.init()
            mixer.music.load(nextmusic)
            mixer.music.play()
            mixer.music.play(-1)