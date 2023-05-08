import dataclasses
import logging

import pyglet
from reactivex.subject import BehaviorSubject, Subject
from reactivex.disposable import CompositeDisposable
from reactivex.operators import publish
import ui_elements
import color_scheme
import widgets

window = pyglet.window.Window(resizable=True)


@window.event
def on_draw():
    window.clear()
    view = controller.get_view()
    view.draw()


class events:
    key = Subject()
    text = Subject()
    mouse = BehaviorSubject((0, 0, 0))
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
    events.mouse.on_next((x, y, False))

@window.event #detected Mausbewegung wenn Buttons gedrückt sind
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    events.mouse_move.on_next((x, y, dx, dy))
    events.mouse.on_next((x, y, buttons))


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
        self.mouse_pos = pyglet.text.Label(font_name="Minecraft", font_size=36, anchor_y="bottom", anchor_x="left", batch=self.batch)
        self.write_letter = pyglet.text.Label(self.active_letter, font_name="Minecraft", font_size=50, anchor_y="center", anchor_x="center", batch=self.batch)

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

        self.back_label = pyglet.text.Label("Press space to go back", batch=self.batch, font_name="Minecraft", font_size=36, anchor_x="center", anchor_y="center", x=window.width//2, y=window.height//2)

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

        self.label = pyglet.text.Label("Press 1 or 2", batch=self.batch, font_name="Minecraft", font_size=36, anchor_x="center", anchor_y="center", x=window.width//2, y=window.height//2)

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
        # x, y, width und height in % angegeben
        self.testButton = ui_elements.BorderedRectangleButton("TestButton", 10, 55, 80, 20, color_scheme.BlackWhite, color_scheme.Font1, events, self.batch)
        self.header = ui_elements.BorderedRectangle("lol nicht klickbar", 0, 80, 100, 20, color_scheme.DarkPurple, color_scheme.Font1, events, self.batch)
        self.testSprite = ui_elements.BorderedClickableSprite("assets/images/popcat.png", 20, 10, 60, 40, color_scheme.BlackWhite, events, self.batch)
        self.borderedSprite = ui_elements.GifButton("assets/images/popcat.gif", 35, 15, 30, 30, 1, True, events, self.batch)

    def get_view(self):
        return self.batch


class StartScreen(Controller):
    def __init__(self):
        self.batch = pyglet.graphics.Batch()

        # Liste, die sämtliche subscriptions fängt, um sie beim Wechseln des Controllers wieder freizugeben
        sublist = []

        # Erstes Layout für den Hauptbildschirm
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, sublist, self.batch)
        self.Header = ui_elements.BorderedRectangle("Die Maschinen-Revolution", 20, 75, 60, 20, color_scheme.BlackWhite, color_scheme.Minecraft, 5, events, sublist, self.batch)
        self.save1 = ui_elements.BorderedRectangleButton("Spielstand 1", 35, 55, 30, 10, color_scheme.BlackWhite, color_scheme.Minecraft, 6, events, sublist, self.batch)
        self.save2 = ui_elements.BorderedRectangleButton("Spielstand 2", 35, 42.5, 30, 10, color_scheme.BlackWhite, color_scheme.Minecraft, 6, events, sublist, self.batch)
        self.save3 = ui_elements.BorderedRectangleButton("Spielstand 3", 35, 30, 30, 10, color_scheme.BlackWhite, color_scheme.Minecraft, 6, events, sublist, self.batch)
        self.delete_save1 = ui_elements.BorderedRectangleButton("Neu", 67.5, 55, 12.5, 10, color_scheme.BlackWhite, color_scheme.Minecraft, 20, events, sublist, self.batch)
        self.delete_save2 = ui_elements.BorderedRectangleButton("Neu", 67.5, 42.5, 12.5, 10, color_scheme.BlackWhite, color_scheme.Minecraft, 20, events, sublist, self.batch)
        self.delete_save3 = ui_elements.BorderedRectangleButton("Neu", 67.5, 30, 12.5, 10, color_scheme.BlackWhite, color_scheme.Minecraft, 20, events, sublist, self.batch)

        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        sublist.extend((self.save1.clicked.subscribe(lambda _: self.save_clicked(1)),
                        self.save2.clicked.subscribe(lambda _: self.save_clicked(2)),
                        self.save3.clicked.subscribe(lambda _: self.save_clicked(3)),
                        self.delete_save1.clicked.subscribe(lambda _: self.delete_save(1)),
                        self.delete_save2.clicked.subscribe(lambda _: self.delete_save(2)),
                        self.delete_save3.clicked.subscribe(lambda _: self.delete_save(3))))
        self.disposable = CompositeDisposable(sublist)

        self.save_selected = Subject()




    def save_clicked(self, data):  # Wird getriggert, wenn ein Spielstand ausgewählt wird
        # save suchen und auswählen
        logging.warning(data)
        self.save_selected.on_next("save")

    def delete_save(self, data):  # Wird getriggert, wenn ein Spielstand gelöscht werden soll
        # datenbank stuff
        #  save löschen
        #  neuen erstelleln
        self.save_selected.on_next("save")
        logging.warning(("Deleting Save", data))

    def dispose_subs(self):  # Muss getriggert werden, wenn der Screen gewechselt wird.
        self.disposable.dispose()

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch


class RichardController(Controller):
    def __init__(self):
        self.scaffold = widgets.FillBorder((255,) * 4, 30, (55, 55, 0, 255), widgets.ClampSize(100, 100, 150, 150, widgets.Text("Bruh", "Arcard", 36, (255,) * 4)))
        self.scaffold.layout(0, 0, window.width, window.height)

    def get_view(self):
        b = pyglet.graphics.Batch()
        self.stuff = self.scaffold.fill_batch(b)
        return b


# controller = GameController()
# controller = JanekController()
controller = StartScreen()
# controller = RichardController()

pyglet.app.run(1/30)
