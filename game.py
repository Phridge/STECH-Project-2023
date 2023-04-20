import pyglet
from reactivex.subject import BehaviorSubject, Subject
from reactivex.operators import publish
import ui_elements
import color_scheme

window = pyglet.window.Window(resizable=False)


@window.event
def on_draw():
    window.clear()
    view = controller.get_view()
    view.draw()


class events:
    key = Subject()
    text = Subject()
    mouse = BehaviorSubject((0, 0))
    mouse_move = Subject()
    mouse_button = Subject()
    size = BehaviorSubject((window.width, window.height))


@window.event
def on_key_press(keycode, mods):
    events.key.on_next((keycode, mods))


@window.event
def on_text(text):
    events.text.on_next(text)


@window.event #detected Mausbewegung wenn keine Buttons gedrückt sind
def on_mouse_motion(x, y, dx, dy):
    events.mouse_move.on_next((x, y, dx, dy))
    events.mouse.on_next((x, y))

@window.event #detected Mausbewegung wenn Buttons gedrückt sind
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    events.mouse_move.on_next((x, y, dx, dy))
    events.mouse.on_next((x, y))


@window.event
def on_mouse_press(x, y, button, modifiers):
    events.mouse_button.on_next((True, x, y, button))


@window.event
def on_mouse_release(x, y, button, modifiers):
    events.mouse_button.on_next((False, x, y, button))


@window.event
def on_resize(w, h):
    events.size.on_next((w, h))



class Controller:
    def get_view(self):
        raise NotImplementedError


class Controller1(Controller):
    def __init__(self):
        def rchar():
            import random
            return random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

        self.active_letter = rchar()

        self.batch = pyglet.graphics.Batch()
        self.mouse_pos = pyglet.text.Label(font_name="Arial", font_size=36, anchor_y="bottom", anchor_x="left", batch=self.batch)
        self.write_letter = pyglet.text.Label(self.active_letter, font_name="Arial", font_size=50, anchor_y="center", anchor_x="center", batch=self.batch)

        def mouse(data):
            self.mouse_pos.text = str(data)

        def size(data):
            self.write_letter.x, self.write_letter.y = data[0] // 2, data[1] // 2

        def on_input(text):
            if self.active_letter == text:
                self.write_letter.text = self.active_letter = rchar()

        events.mouse.subscribe(mouse)
        events.size.subscribe(size)
        events.text.subscribe(on_input)

    def get_view(self):
        return self.batch


class Controller2(Controller):

    def __init__(self):
        self.on_back = Subject()

        self.batch = pyglet.graphics.Batch()

        self.back_label = pyglet.text.Label("Press space to go back", batch=self.batch, font_name="Arial", font_size=36, anchor_x="center", anchor_y="center", x=window.width//2, y=window.height//2)

        self.key_subscrption = events.key.subscribe(self.key_press)

    def key_press(self, data):
        key, mods = data
        if key == pyglet.window.key.SPACE:
            self.on_back.on_next(None)
            self.key_subscrption.dispose()

    def get_view(self):
        return self.batch


class GameController(Controller):
    def __init__(self):
        self.current = None


        self.batch = pyglet.graphics.Batch()

        self.label = pyglet.text.Label("Press 1 or 2", batch=self.batch, font_name="Arial", font_size=36, anchor_x="center", anchor_y="center", x=window.width//2, y=window.height//2)

        events.key.subscribe(self.key_press)


    def key_press(self, data):
        if self.current is not None:
            return

        key, mods = data

        if key == pyglet.window.key._1:
            self.current = Controller1()
        elif key == pyglet.window.key._2:
            self.current = Controller2()
            self.current.on_back.subscribe(lambda _: setattr(self, "current", None))


    def get_view(self):
        return self.batch if self.current is None else self.current.get_view()



class JanekController(Controller):
    def __init__(self):
        self.batch = pyglet.graphics.Batch()
        self.testButton = ui_elements.BorderedRectangleButton("TestButton", 50, 50, 100, 50, color_scheme.color_scheme1, color_scheme.font_scheme1, events, self.batch)

    def get_view(self):
        return self.batch




controller = JanekController()


pyglet.app.run(1/30)
