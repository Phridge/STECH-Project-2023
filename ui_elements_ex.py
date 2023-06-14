import dataclasses
from collections import namedtuple
from functools import partial
from typing import Any

import pyglet.shapes
import reactivex
from reactivex import Observer, using, Observable
from reactivex.disposable import CompositeDisposable, SerialDisposable

from events import Disposable, Var, Event


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
    """
    Mapping-Operator für Rect-Observables.

    Wählt eine Innere Region aus einem Rect aus. Sinnvoll für UI Elements.

    Verwendung:

        fenster_observable.pipe(
            map_inner_perc(10, 10, 30, 40)
        )

    """
    return rmap(lambda r: r.inner_perc(p_x, p_y, p_w, p_h))


def map_center_anchor():
    return rmap(Rect.center_anchor)


def rx(v, default=None):
    """
    Wrappt das argument, sofern es nicht reactivex.Observable ist, in ein Observable.
    :param default: falls v None ist, wird default eingesetzt
    :param v: ein Wert
    :return: v falls v Observable ist, ansonsten ein reactivex.just(v) Observable
    """
    return v if isinstance(v, reactivex.Observable) else reactivex.just(v if v is not None else default)


def position_pyglet_shape(shape, rect):
    shape.x, shape.y, shape.width, shape.height = rect


def position_pyglet_text(text, rect):
    text.x, text.y = rect.x, rect.y


@dataclasses.dataclass
class Style:
    """
    Zusammenfassung für 3 werte, die typischerweise an UI-Elemente übergeben werden.
    """
    color: Any  # so nen color_scheme.color_scheme objekt
    font: str
    font_size: float

    def scale_font_size(self, factor):
        return Style(self.color, self.font, self.font_size * factor)


class UIElement(Disposable):
    def __init__(self):
        self._subs = CompositeDisposable()


class BorderedLabel(UIElement):
    """
    Text mit rand.
    """
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


class TypeTracker(Disposable):
    """
    Um einggebbare Texte zu realisieren.
    """
    def __init__(self, preset_text, typed):

        def on_subscribe(subscriber, scheduler):
            typer_disposable = SerialDisposable()

            def text_typer(preset):
                _preset = preset

                def on_type(text):
                    nonlocal _preset
                    if text == _preset[0]:
                        _preset = _preset[1:]
                    if len(_preset) == 0:
                        self.finished.on_next(None)
                        _preset = preset
                    subscriber.on_next(_preset)
                subscriber.on_next(_preset)

                typer_disposable.disposable = typed.subscribe(on_type)

            return CompositeDisposable(
                typer_disposable,
                preset_text.subscribe(text_typer)
            )

        self.text = Observable(on_subscribe)
        self.finished = Event()


class Button(UIElement):
    """
    Anklickbarer und Eingebbarer Button.
    """
    def __init__(self, text, pos, style, events, on_click: Observer, type_in=True, batch=None, group=None):
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

        self._subs.add(text.subscribe(print))
        # eingabetracker wie von janek
        type_tracker = TypeTracker(text, events.text if type_in else reactivex.never())
        self._subs.add(type_tracker.text.subscribe(partial(setattr, text_layout, "text")))
        self._subs.add(type_tracker.finished.subscribe(on_click))

        self.down = False
        self.hover = False


        def update_style():
            """
            Je nach aktuellen zustand wird aussehen geändert.
            """
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
    """
    Button, der zwei zustände hat.
    """
    def __init__(self, text, pos, style, events, type_in=True, batch=None, group=None):
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

        def on_typed_in(_):
            self.toggle.on_next(not self.toggle.value)
            update_style()

        type_tracker = TypeTracker(text, events.text if type_in else reactivex.never())
        self._subs.add(type_tracker.text.subscribe(partial(setattr, text_layout, "text")))
        self._subs.add(type_tracker.finished.subscribe(on_typed_in))

        def update_style():
            """
            Je nach aktuellen zustand wird aussehen geändert.
            """
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
    """
    Einfarbiges Rechteck.
    """
    def __init__(self, pos, color, batch=None, group=None):
        super().__init__()
        pos, color = rx(pos), rx(color)

        rect = pyglet.shapes.Rectangle(0, 0, 0, 0, (0,)*4, batch, group)
        self._subs.add(pos.subscribe(partial(position_pyglet_shape, rect)))
        self._subs.add(color.subscribe(partial(setattr, rect, "color")))
