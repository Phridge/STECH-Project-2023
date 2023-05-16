from functools import partial
from typing import Optional

import pyglet
from pyglet.graphics import Group
from reactivex import Observable, concat, just
from reactivex.operators import scan, combine_latest, map as rmap, filter as rfilter, merge, do_action, share
from reactivex.disposable import MultipleAssignmentDisposable as MAD, CompositeDisposable

import events
import input_tracker
from tools import save_and_open
from ui_elements_ex import Rect, rx, Style, position_pyglet_shape, position_pyglet_text, map_border, map_center_anchor

from controller import Controller
import numpy as np


class InputBox(Controller):
    def __init__(self, text: str | Observable, pos: Rect | Observable, style: Style, events: events.Events, batch=None, group: Group=None):
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

        # ob die der textracker zustand gespeichert wurde
        has_saved = False

        def display_text_tracker(tt: input_tracker.TextTracker):
            text_correct = tt.last_input_correct

            document.text = tt.current_text
            # mögliche verbesserung s. pyglet.text.Caret zeile 388 #update
            caret.position = np.array(text_layout.get_point_from_position(tt.current_position)) + np.array(text_layout.position[:2]) + np.array((0, text_layout.height)) + caret_off


            typed_text_style = dict(
                font_name=style.font,
                font_size=style.font_size,
                color=(0, 255, 0, 255) if text_correct else (255, 0, 0, 255))
            text_style = dict(
                font_name=style.font,
                font_size=style.font_size,
                color=style.color.text)

            document.set_style(0, tt.current_position, typed_text_style)
            document.set_style(tt.current_position, len(document.text), text_style)

        def update_caret_pos(data):
            tt, rect = data
            caret.position = np.array(text_layout.get_point_from_position(tt.current_position)) + np.array((rect.x, rect.y)) + np.array((0, rect.h)) + caret_off

        tt_sub = MAD()
        self._subs.add(tt_sub)

        def init_text_tracker(text):
            tt = input_tracker.TextTracker(text)
            tt.start_timer()
            nonlocal has_saved
            has_saved = False

            def accept_char(cmd):
                nonlocal has_saved
                tt.accept_char(cmd)
                if tt.string_finished and not has_saved:
                    try:
                        save_and_open.save_text_tracker(0, 0, "sandbox", tt)
                    except Exception as e:
                        print("Konnte nicht gespeichert werden")
                        raise e
                    else:
                        print("Erfolgreich gespeichert")
                    has_saved = True
                return tt

            tt_obs = concat(
                just(tt),
                events.text.pipe(
                    rmap(accept_char),
                    share()
                )
            )

            tt_sub.disposable = CompositeDisposable([
                tt_obs.subscribe(display_text_tracker),
                tt_obs.pipe(
                    combine_latest(text_layout_pos),
                ).subscribe(update_caret_pos),
            ])

        self._subs.add(text.subscribe(init_text_tracker))

