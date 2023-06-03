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
    """
    Animiert einen Wert von lo nach hi über gegebene Zeit.
    :param lo: startwert.
    :param hi: endwert.*--
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

        # hintergrund
        self.gif = ui_elements.Gif("assets/images/port.gif", 0, 0, 100, 100, 30, True, self.events, self.batch, background)

        # Player-Objekt
        # player = Player(self.events, self.batch, 20, 40, 20, 30)


        # Spieler-Objekt. Bis is eine Position erhält, ist es nicht sichtbar.
        self.p = ThePlayer(batch=self.batch, group=foreground)
        # Region, in dem sich der spieler bewegen darf. Die untere kante stellt den laufsteg dar.
        player_area = pos.pipe(
            map_inner_perc(0, 40, 100, 60)
        )

        # event, welches von der Machine s. unten den anzuzeigenden Text erhält-
        text = Event()

        # um die Spielereingaben Textübergreifend zu sammeln und in die Datenbank zu speicher.
        input_analysis = InputAnalysis()
        self.input_box = InputBox(text, pos.pipe(map_inner_perc(10, 5, 80, 20)), style, events, input_analysis, batch=self.batch, group=foreground)
        # ist ein Text fertig geschrieben, wird die Machine um einen Schritt vorangebracht.
        self._subs.add(
            self.input_box.text_tracker.pipe(
                rfilter(lambda tt: tt.is_finished)
            ).subscribe(lambda _: machine.next())
        )

        # Überschrift.
        self.header = ui_elements.BorderedRectangle("Level 1: Der Hafen der Freiheit", 20, 80, 60, 20, self.events.color_scheme, color_scheme.Minecraft, 2, self.events, self.batch)

        class Machine:
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

        def display_text(display_text):
            """
            Factory-Funktion, um einfach den nächsten Text in der Input-Box anzuzeigen.
            :param display_text: Zu schreibender Text.
            :return: eine Funktion, die von der Machine ausgeführt werden kann.
            """
            return lambda: text.on_next(display_text)

        def player_entry():
            """
            Eröffnung des Levels.

            Der Bildschirm faded von Schwarz zu durchsichtig, und der Spieler läuft von der Linken seite ein.
            :return: Nachher zu löschenden Ressourcen.
            """
            # farbanimation
            color = animate(255, 0, 3.0, events.update, lambda o: (0, 0, 0, int(o)))
            # spielerpositionsanimation.
            # Sieht kompliziert aus, da noch die Position des Laufstegs mit berücksichtigt werden muss.
            player_pos = animate(-300, 100, 5.0, events.update).pipe(
                do_action(on_completed=lambda: machine.next()),  # wenn die animation durch ist, nächster Zustand
                combine_latest(player_area),
                starmap(lambda xoff, area: Rect(xoff, 0, 150, 150).offset(area)),
            )
            # Das Rechteck für den FAde
            overlay_rect = Rectangle(pos, color, self.batch, overlay)

            # den Spieler zum Laufen bringen.
            self.p.running_speed.on_next(2.0)
            return CompositeDisposable(
                overlay_rect,
                player_pos.subscribe(self.p.pos),
                Disposable(lambda: self.p.running_speed.on_next(0.0))  # wenn fertig, dann spieler stoppen.
            )

        def player_exit():
            """
            Wie player_entry, nur umgekehrt.
            """
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

        # Erstellung der State Machine aus allen nötigen Zuständen:
        # Spieler entry
        # dann die ganzen texte
        # dann Spieler exit
        machine = Machine(
            [player_entry]
            + [display_text(text) for text in self.TEXTS]
            + [player_exit]
        )


    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch

    def play_music(self, nextmusic):
        with contextlib.suppress(pygame.error):
            mixer.init()
            mixer.music.load(nextmusic)
            mixer.music.play()
            mixer.music.play(-1)