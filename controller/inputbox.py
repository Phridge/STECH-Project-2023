from functools import partial

import pyglet
from reactivex import Observable, concat, just
from reactivex.operators import scan, combine_latest

import events
from ui_elements_ex import Rect, rx, Style, position_pyglet_shape, position_pyglet_text, map_border, map_center_anchor

from controller import Controller


class InputBox(Controller):
    def __init__(self, text: str | Observable, pos: Rect | Observable, style: Style, events: events.Events, batch=None, group=None):
        super().__init__()
        text, pos = rx(text), rx(pos)

        # Rand
        border = pyglet.shapes.Rectangle(*Rect.zero(), style.color.border, batch, group)
        self._subs.add(pos.subscribe(partial(position_pyglet_shape, border)))

        # innere füllung
        fill = pyglet.shapes.Rectangle(*Rect.zero(), style.color.color, batch, group)
        fill_pos = pos.pipe(map_border(style.color.border_thickness))
        self._subs.add(fill_pos.subscribe(partial(position_pyglet_shape, fill)))

        # Text
        document = pyglet.text.document.FormattedDocument()
        self.text_layout = text_layout = pyglet.text.layout.IncrementalTextLayout(document, 1, 0, True, batch=batch, group=group)
        self._subs.add(fill_pos.pipe(map_border(5)).subscribe(partial(position_pyglet_shape, text_layout)))

        typed_text = concat(just(""), events.text.pipe(
            scan(str.__add__, "")
        ))

        def update_text(data):
            text, typed_text = data

            text_correct = len(typed_text) > 0 and text[len(typed_text)-1] == typed_text[-1]

            document.text = text

            typed_text_style = dict(
                font_name=style.font,
                font_size=style.font_size,
                color=(0, 255, 0, 255) if text_correct else (255, 0, 0, 255))
            text_style = dict(
                font_name=style.font,
                font_size=style.font_size,
                color=style.color.text)

            document.set_style(0, len(typed_text), typed_text_style)
            document.set_style(len(typed_text), len(text), text_style)

        self._subs.add(text.pipe(combine_latest(typed_text)).subscribe(update_text))

