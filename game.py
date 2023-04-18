import pyglet
from reactivex.subject import BehaviorSubject, Subject
from reactivex.operators import publish



window = pyglet.window.Window(resizable=False)



drawable = None


def set_drawable(d):
    assert hasattr(d, "draw")
    global drawable
    drawable = d


@window.event
def on_draw():
    window.clear()
    if drawable:
        drawable.draw()


class events:
    key_press = Subject()
    text = Subject()
    mouse = BehaviorSubject((0, 0))
    mouse_move = Subject()
    size = BehaviorSubject((window.width, window.height))


@window.event
def on_key_press(keycode, mods):
    events.key_press.on_next((keycode, mods))


@window.event
def on_text(text):
    events.text.on_next(text)


@window.event
def on_mouse_motion(x, y, dx, dy):
    events.mouse_move.on_next((x, y, dx, dy))
    events.mouse.on_next((x, y))



@window.event
def on_resize(w, h):
    events.size.on_next((w, h))


class TestController:
    def __init__(self):
        def chars():
            import random
            while True:
                yield random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

        self.char_iter = chars()
        self.active_letter = next(self.char_iter)

        self.batch = pyglet.graphics.Batch()
        self.mouse_pos = pyglet.text.Label("", font_name="Arial", font_size=36, anchor_y="bottom", anchor_x="left", batch=self.batch)
        self.write_letter = pyglet.text.Label(self.active_letter, font_name="Arial", font_size=50, anchor_y="center", anchor_x="center", batch=self.batch)

        def mouse(data):
            self.mouse_pos.text = str(data)

        def size(data):
            self.write_letter.x, self.write_letter.y = data[0] // 2, data[1] // 2
            return
            self.view.x, self.view.y = 0, 0

        def on_input(text):
            if self.active_letter == text:
                self.write_letter.text = self.active_letter = next(self.char_iter)

        events.mouse.subscribe(mouse)
        events.size.subscribe(size)
        events.text.subscribe(on_input)

        set_drawable(self.batch)


controller = TestController()


pyglet.app.run(1/30)
