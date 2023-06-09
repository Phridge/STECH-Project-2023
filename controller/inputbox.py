from functools import partial
from typing import Optional

import pyglet
from pyglet.graphics import Group
from reactivex import Observable, concat, just
from reactivex.operators import scan, combine_latest, map as rmap, filter as rfilter, merge, do_action, share
from reactivex.disposable import SerialDisposable, CompositeDisposable, Disposable

from events import Events, Event
import input_tracker
from tools import save_and_open
from ui_elements_ex import Rect, rx, Style, position_pyglet_shape, position_pyglet_text, map_border, map_center_anchor

from controller import Controller
import numpy as np


class InputBox(Controller):
    """
    Eingagebox, die auf dem Bildschirm positioniert werden kann.
    Reagiert auf Änderungen des Textes und eigabe durch den Nutzer über Observables,
    und nutzt einen TextTracker im hintergrund, um den Eingabefortschritt zu modellieren.
    """
    def __init__(self, text: str | Observable, pos: Rect | Observable, style: Style, events: Events, input_analysis=None, batch=None, group: Group=None):
        """
        Erstelle eine Inputbox.
        :param text: Text, kann auch ein Observable mit Text sein.
        :param pos: Position (auch gerne Observable)
        :param style: Style-Objket fürs aussehen.
        :param events: Events-Objekt
        :param input_analysis: Ein InputAnalysis-Objekt, welches Statistiken auswertet während der Eingabe. Kann auch
        weggelassen werden, sodass keine sTatistiken angelegt werden.
        :param batch: Batch zum reinzeichen.
        :param group: Gruppe der Inputbox.
        """
        super().__init__()
        text, pos = rx(text), rx(pos)
        background = Group(0, parent=group)
        foreground = Group(1, parent=group)
        # Rand
        border = pyglet.shapes.Rectangle(*Rect.zero(), style.color.border, batch, background)
        self._subs.add(pos.subscribe(partial(position_pyglet_shape, border)))

        # innere füllung
        fill = pyglet.shapes.Rectangle(*Rect.zero(), style.color.color, batch, background)
        fill_pos = pos.pipe(map_border(style.color.border_thickness))
        self._subs.add(fill_pos.subscribe(partial(position_pyglet_shape, fill)))

        # Text
        document = pyglet.text.document.FormattedDocument()
        self.text_layout = text_layout = pyglet.text.layout.IncrementalTextLayout(document, 1, 0, True, batch=batch, group=background)
        text_layout_pos = fill_pos.pipe(map_border(5))
        self._subs.add(text_layout_pos.subscribe(partial(position_pyglet_shape, text_layout)))

        # cursor
        caret = pyglet.shapes.Rectangle(*Rect.zero(), style.color.text, batch, foreground)
        caret.height, caret.width = style.font_size * 1.4, 2
        caret_off = np.array((-3, -3))

        # Text-tracker-Event, in das bei jeder änderung von abhängigketen (text und eigegebener Buchstabe) ein neuer Text-
        # Tracker reingeschickt wird
        self.text_tracker = Event()

        def display_text_tracker(tt: input_tracker.TextTracker):
            """
            Visualisiert den aktuellen Zustand des TExttrackers im UI.
            :param tt: der Texttracker
            """
            # letzte eingabe korrekt?
            text_correct = tt.last_input_correct

            # text in der Textanzeige an sich aktualisieren
            document.text = tt.current_text
            # cursor positionieren.
            # mögliche verbesserung s. pyglet.text.Caret zeile 388 #update
            caret.position = np.array(text_layout.get_point_from_position(tt.current_position)) + np.array(text_layout.position[:2]) + np.array((0, text_layout.height)) + caret_off

            # für den bisher geschriebenen Text das STyling. Rot wenn zuletzt falsch, grün wenn zuletzt richtig.
            typed_text_style = dict(
                font_name=style.font,
                font_size=style.font_size,
                color=(0, 255, 0, 255) if text_correct else (255, 0, 0, 255))
            # für den rest weiß.
            text_style = dict(
                font_name=style.font,
                font_size=style.font_size,
                color=style.color.text)

            # Styles in der Textanzeige anwenden.
            document.set_style(0, tt.current_position, typed_text_style)
            document.set_style(tt.current_position, len(document.text), text_style)

        def update_caret_pos(data):
            """Funktion wird aufgerufen, um die Position des Cursors anzupassen."""
            tt, rect = data
            caret.position = np.array(text_layout.get_point_from_position(tt.current_position)) + np.array((rect.x, rect.y)) + np.array((0, rect.h)) + caret_off

        tt_sub = SerialDisposable()
        self._subs.add(tt_sub)

        def init_text_tracker(t):
            """
            Jedes mal, wenn ein neuer Text gesendet wird, wird ein neuer Texttracker erstellt. Das passiert in dieser Funktion.
            Da müssen auch jedes mal neue Subscriptions auf die Observables erstell werden, diese werden dann gemeinschaftlich in tt_sub gespeichert.
            :param t: neuer Text.
            """
            # neuer texttracker aus text und aktueller InputAnalysis-Istnanz
            tt = input_tracker.TextTracker(t, input_analysis)

            def accept_char(cmd):
                """
                wird jedes mal aufgerufen, wenn ein buchstabe eingegeben wird. Sendet diese eingabe an den Textracker.
                Ist dieser fertig, werden resourcen verworfen.
                """
                # buchstabe senden
                tt.accept_char(cmd)
                # NEUER TEXTTRACKER!!
                self.text_tracker.on_next(tt)
                # wenn fertig, dann ist ruhe
                # if tt.is_finished:
                #     print("Early Dispose", vars(tt))
                #     tt_sub.disposable = None

            tt_sub.disposable = CompositeDisposable([
                events.text.subscribe(accept_char),  # auf eingaben reagieren
                self.text_tracker.subscribe(display_text_tracker),  # texttracker anzeigen bei änderungen
                self.text_tracker.pipe(
                    combine_latest(text_layout_pos),
                ).subscribe(update_caret_pos),  # cursorposition
            ])

            # initialer texttracker wird gesenet
            self.text_tracker.on_next(tt)

        # auf neue texte reagieren
        self._subs.add(text.subscribe(init_text_tracker))

        # behebt einen Fehler.
        self._subs.add(Disposable(lambda: text_layout.delete()))

