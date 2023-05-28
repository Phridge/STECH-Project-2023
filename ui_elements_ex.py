import dataclasses
from collections import namedtuple
from functools import partial
from typing import Any

import pyglet.shapes
import reactivex
from reactivex import Observer
from reactivex.disposable import CompositeDisposable

from events import Disposable, Var


class Rect(namedtuple("Rect", ["x", "y", "w", "h"])):
    def border(self, width):
        return Rect(self.x + width, self.y + width, max(0, self.w - 2 * width), max(0, self.h - 2 * width))

    def inner_perc(self, p_x, p_y, p_w, p_h):
        return Rect(self.x + (p_x / 100) * self.w, self.y + (p_y / 100) * self.h, self.w * (p_w / 100), self.h * (p_h / 100))

    def center_anchor(self):
        return Rect(self.x + self.w / 2, self.y + self.h / 2, self.w, self.h)

    def offset(self, by):
        return Rect(self.x + by[0], self.y + by[1], self.w, self.h)

    @staticmethod
    def zero():
        return Rect(0, 0, 0, 0)


from reactivex.operators import map as rmap


def map_border(width):
    return rmap(lambda r: r.border(width))


def map_inner_perc(p_x, p_y, p_w, p_h):
    return rmap(lambda r: r.inner_perc(p_x, p_y, p_w, p_h))


def map_center_anchor():
    return rmap(Rect.center_anchor)


def rx(v):
    return v if isinstance(v, reactivex.Observable) else reactivex.just(v)


def position_pyglet_shape(shape, rect):
    shape.x, shape.y, shape.width, shape.height = rect


def position_pyglet_text(text, rect):
    text.x, text.y = rect.x, rect.y


@dataclasses.dataclass
class Style:
    color: Any
    font: str
    font_size: float


class UIElement(Disposable):
    def __init__(self):
        self._subs = CompositeDisposable()


class BorderedLabel(UIElement):
    def __init__(self, text, pos, style: Style, batch=None, group=None):
        super().__init__()
        text, pos = rx(text), rx(pos)

        # Rand
        border = pyglet.shapes.Rectangle(*Rect.zero(), style.color.border, batch, group)
        self._subs.add(pos.subscribe(partial(position_pyglet_shape, border)))

        # innere füllung
        fill = pyglet.shapes.Rectangle(*Rect.zero(), style.color.color, batch, group)
        self._subs.add(pos.pipe(map_border(style.color.border_thickness)).subscribe(partial(position_pyglet_shape, fill)))

        # Text
        text_layout = pyglet.text.Label("", style.font, style.font_size, color=style.color.text, anchor_x="center", anchor_y="center", batch=batch, group=group)
        self._subs.add(pos.pipe(map_center_anchor()).subscribe(partial(position_pyglet_text, text_layout)))
        self._subs.add(text.subscribe(partial(setattr, text_layout, "text")))


class Button(UIElement):
    def __init__(self, text, pos, style, events, on_click: Observer, batch=None, group=None):
        super().__init__()
        text, pos = rx(text), rx(pos)
        self._subs.add(on_click)

        # Rand
        border = pyglet.shapes.Rectangle(*Rect.zero(), style.color.border, batch, group)
        self._subs.add(pos.subscribe(partial(position_pyglet_shape, border)))

        # innere füllung
        fill = pyglet.shapes.Rectangle(*Rect.zero(), style.color.color, batch, group)
        self._subs.add(pos.pipe(map_border(style.color.border_thickness)).subscribe(partial(position_pyglet_shape, fill)))

        # Text
        text_layout = pyglet.text.Label("", style.font, style.font_size, color=style.color.text, anchor_x="center", anchor_y="center", batch=batch, group=group)
        self._subs.add(pos.pipe(map_center_anchor()).subscribe(partial(position_pyglet_text, text_layout)))
        self._subs.add(text.subscribe(partial(setattr, text_layout, "text")))

        self.down = False
        self.hover = False


        def update_style():
            if self.down:
                fill.color = style.color.click
                border.color = style.color.click_border
                text_layout.color = style.color.click_text
            elif self.hover:
                fill.color = style.color.hover
                border.color = style.color.hover_border
                text_layout.color = style.color.hover_text
            else:
                fill.color = style.color.color
                border.color = style.color.hover_border
                text_layout.color = style.color.hover_text

        def handle_mouse(data):
            x, y, *_ = data
            if border.x <= x < border.x + border.width and border.y <= y < border.y + border.height:
                if not self.hover:
                    self.hover = True
                    update_style()
            else:
                if self.hover:
                    self.hover = False
                    update_style()

        def handle_mouse_button(data):
            down, x, y, button = data
            if down and self.hover and button & 1:
                if not self.down:
                    self.down = True
                    update_style()
            else:
                if self.down:
                    if self.hover:
                        on_click.on_next(None)
                    self.down = False
                    update_style()

        self._subs.add(events.mouse.subscribe(handle_mouse))
        self._subs.add(events.mouse_button.subscribe(handle_mouse_button))


class ToggleButton(UIElement):
    def __init__(self, text, pos, style, events, batch=None, group=None):
        super().__init__()
        text, pos = rx(text), rx(pos)

        # Rand
        border = pyglet.shapes.Rectangle(*Rect.zero(), style.color.border, batch, group)
        self._subs.add(pos.subscribe(partial(position_pyglet_shape, border)))

        # innere füllung
        fill = pyglet.shapes.Rectangle(*Rect.zero(), style.color.color, batch, group)
        self._subs.add(pos.pipe(map_border(style.color.border_thickness)).subscribe(partial(position_pyglet_shape, fill)))

        # Text
        text_layout = pyglet.text.Label("", style.font, style.font_size, color=style.color.text, anchor_x="center", anchor_y="center", batch=batch, group=group)
        self._subs.add(pos.pipe(map_center_anchor()).subscribe(partial(position_pyglet_text, text_layout)))
        self._subs.add(text.subscribe(partial(setattr, text_layout, "text")))

        def update_style():
            if self.toggle.value:
                fill.color = style.color.click
                border.color = style.color.click_border
                text_layout.color = style.color.click_text
            elif self.hover:
                fill.color = style.color.hover
                border.color = style.color.hover_border
                text_layout.color = style.color.hover_text
            else:
                fill.color = style.color.color
                border.color = style.color.hover_border
                text_layout.color = style.color.hover_text

        def handle_mouse(data):
            x, y, *_ = data
            if border.x <= x < border.x + border.width and border.y <= y < border.y + border.height:
                if not self.hover:
                    self.hover = True
                    update_style()
            else:
                if self.hover:
                    self.hover = False
                    update_style()

        def handle_mouse_button(data):
            down, x, y, button = data
            if down and self.hover and button & 1:
                if not self.down:
                    self.down = True
                    update_style()
            else:
                if self.down:
                    self.toggle.on_next(not self.toggle.value)
                    self.down = False
                    update_style()

        self.down = False
        self.hover = False
        self.toggle = Var(False)

        self._subs.add(self.toggle.subscribe(lambda _: update_style()))
        self._subs.add(events.mouse.subscribe(handle_mouse))
        self._subs.add(events.mouse_button.subscribe(handle_mouse_button))

class Rectangle(UIElement):
    def __init__(self, pos, color, batch=None, group=None):
        super().__init__()
        pos, color = rx(pos), rx(color)

        rect = pyglet.shapes.Rectangle(0, 0, 0, 0, (0,)*4, batch, group)
        self._subs.add(pos.subscribe(partial(position_pyglet_shape, rect)))
        self._subs.add(color.subscribe(partial(setattr, rect, "color")))
