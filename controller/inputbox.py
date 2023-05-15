from functools import partial

import pyglet
from pyglet.graphics import Group
from reactivex import Observable, concat, just
from reactivex.operators import scan, combine_latest, map as rmap, filter as rfilter, merge, do_action
from reactivex.disposable import MultipleAssignmentDisposable as MAD

import events
import input_tracker
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
        self._subs.add(fill_pos.pipe(map_border(5)).subscribe(partial(position_pyglet_shape, text_layout)))

        caret = pyglet.shapes.Rectangle(*Rect.zero(), style.color.text, batch, foreground)
        caret.height, caret.width = style.font_size * 1.4, 2
        caret_off = np.array((-3, -3))

        def display_text_tracker(tt: input_tracker.TextTracker):
            text_correct = tt.last_input_correct

            document.text = tt.current_text
            print(text_layout.get_point_from_position(tt.current_position))
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

        tt_sub = MAD()
        self._subs.add(tt_sub)

        def init_text_tracker(text):
            tt = input_tracker.TextTracker(text)
            tt.start_timer()

            def accept_char(cmd):
                tt.accept_char(cmd)
                return tt

            tt_sub.disposable = concat(
                just(tt),
                events.text.pipe(
                    rmap(accept_char),
                )
            ).subscribe(display_text_tracker)

        self._subs.add(text.subscribe(init_text_tracker))

