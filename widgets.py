import abc

import pyglet



def new_key():
    return object()


class Widget(abc.ABC):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0

    def preferred_size(self, w, h):
        return 0, 0

    def layout(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    def fill_batch(self, batch):
        pass

    def get_interactions(self, env, collector):
        pass

    def is_hit(self, x, y):
        return None


class MixinWidget(Widget, abc.ABC):
    def __init__(self, inner):
        super().__init__()
        self.inner = inner

    def preferred_size(self, w, h):
        return self.inner.preferred_size(w, h)

    def layout(self, x, y, w, h):
        self.inner.layout(x, y, w, h)
        self.x, self.y, self.w, self.h = x, y, w, h

    def fill_batch(self, batch):
        return self.inner.fill_batch(batch)

    def get_interactions(self, env, collector):
        return self.inner.get_interactions(env, collector)

    def is_hit(self, x, y):
        return self.inner.is_hit(x, y)


class Fill(Widget):
    def __init__(self, color):
        super().__init__()
        self.color = color

    def fill_batch(self, batch):
        return [pyglet.shapes.Rectangle(self.x, self.y, self.w, self.h, self.color, batch)]


class FillBorder(MixinWidget):
    def __init__(self, border_color, border_width, fill_color, inner):
        super().__init__(inner)
        self.bc = border_color
        self.bw = border_width
        self.fc = fill_color

    def preferred_size(self, w, h):
        iw, ih = self.inner.preferred_size(max(0, w - 2 * self.bw), max(0, h - 2 * self.bw))
        return iw + 2 * self.bw, ih + 2 * self.bw

    def layout(self, x, y, w, h):
        self.x, self.y = x, y
        self.inner.layout(x + self.bw, y + self.bw, max(0, w - 2 * self.bw), max(0, h - 2 * self.bw))
        self.w, self.h = self.inner.w + 2 * self.bw, self.inner.h + 2 * self.bw

    def fill_batch(self, batch):
        shape = pyglet.shapes.BorderedRectangle(self.x, self.y, self.w, self.h, self.bw, self.fc, self.bc, batch)
        return [shape] + self.inner.fill_batch(batch)


class Text(Widget):
    def __init__(self, text, font, font_size, color):
        super().__init__()
        self.text = text
        self.font = font
        self.font_size = font_size
        self.color = color

    def fill_batch(self, batch):
        return [pyglet.text.Label(self.text, self.font, self.font_size, color=self.color, x=self.x, y=self.y, width=self.w, height=self.h, batch=batch)]


class ClampSize(MixinWidget):
    def __init__(self, min_w, max_w, min_h, max_h, inner):
        super().__init__(inner)
        self.min_w, self.min_h = min_w, min_h
        self.max_w, self.max_h = max_w, max_h

    def preferred_size(self, w, h):
        return self.inner.preferred_size(max(min(w, self.max_w), self.min_w), max(min(h, self.max_h), self.min_h))

    def layout(self, x, y, w, h):
        self.inner.layout(x, y, max(min(w, self.max_w), self.min_w), max(min(h, self.max_h), self.min_h))
        self.x, self.y = x, y
        self.w, self.h = self.inner.w, self.inner.h


class HitBox(MixinWidget):
    def __init__(self, key, inner):
        super().__init__(inner)
        self.key = key

    def is_hit(self, x, y):
        return self.inner.is_hit(x, y) or (self.x <= x < self.x + self.w and self.y <= y < self.y + self.h and self.key)


class CompositeWidget(Widget, abc.ABC):
    def __init__(self):
        super().__init__()
        self._inner = None

    @property
    def inner(self):
        if not self._inner:
            self._inner = self.render()
        return self._inner

    def _set_dirty(self):
        self._inner = None

    def render(self):
        raise NotImplementedError

    def fill_batch(self, batch):
        return self.inner.fill_batch(batch)

    def preferred_size(self, w, h):
        return self.inner.preferred_size(w, h)

    def layout(self, x, y, w, h):
        self.inner.layout(x, y, w, h)
        self.x, self.y, self.w, self.h = x, y, w, h

    def get_interactions(self, env, collector):
        return self.inner.get_interactions(env, collector)

    def is_hit(self, x, y):
        return self.inner.is_hit(x, y)
