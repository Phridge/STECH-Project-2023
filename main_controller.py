import logging

import pyglet
from reactivex.subject import BehaviorSubject, Subject
from reactivex.disposable import CompositeDisposable
import color_scheme

from controller.settings import SettingsScreen
from controller.statistics import StatisticsScreen
from controller.start_screen import StartScreen
from controller.home_screen import HomeScreen
from controller.error_screen import ErrorScreen
from controller.delete_save_screen import DeleteSaveScreen
from controller.pause_screen import PauseScreen

# Beispiel-Bildschirm
from controller.template_screen import TemplateScreen

window = pyglet.window.Window(resizable=False)


class Events:
    key = Subject()
    text = Subject()
    mouse = BehaviorSubject((0, 0, 0))
    mouse_move = Subject()
    mouse_button = Subject()
    size = BehaviorSubject((window.width, window.height))
    color_scheme = color_scheme.BlackWhite

@window.event
def on_draw():
    window.clear()
    view = controller.get_view()
    view.draw()


@window.event
def on_key_press(keycode, mods):
    Events.key.on_next((keycode, mods))


@window.event
def on_text(text):
    Events.text.on_next(text)


@window.event  #detected Mausbewegung wenn keine Buttons gedrückt sind
def on_mouse_motion(x, y, dx, dy):
    Events.mouse_move.on_next((x, y, dx, dy))
    Events.mouse.on_next((x, y, False))


@window.event  #detected Mausbewegung wenn Buttons gedrückt sind
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    Events.mouse_move.on_next((x, y, dx, dy))
    Events.mouse.on_next((x, y, buttons))


@window.event
def on_mouse_press(x, y, button, modifiers):
    Events.mouse_button.on_next((True, x, y, button))


@window.event
def on_mouse_release(x, y, button, modifiers):
    Events.mouse_button.on_next((False, x, y, button))


@window.event
def on_resize(w, h):
    Events.size.on_next((w, h))


'''
ab hier beginnt der zentrale Controller.
Jeder Controller zeigt eine "Seite", siehe SiteMap.
Es darf also nur ein Controller gleichzeitig aktiv sein
'''


controller = StartScreen(Events)  # Setzt StartBildschirm als initialen Controller
sublist = []  # erstellte eine sublist, die ermöglicht Subscriptions wieder aufzuheben


def load_controller(data):
    """
    Lädt einen neuen Controller und trennt alle Subscriptions zum alten Controller.

    :param data: der Name des neuen Controllers als string, und eventuell ein parameter (new_controller, *parameter)
    """
    new_controller, *parameter = data  # entpackt data in die Einzelkomponenten

    # löscht alle subscriptions im main_controller
    global sublist
    CompositeDisposable(sublist).dispose()
    sublist = []  # leert die sublist

    # löscht die subscriptions des alten Controllers
    global controller
    controller.dispose_subs()

    # Schlüsselt den Namen des nächsten Controllers auf und weist den neuen controller zu
    if new_controller == "Restart":
        pyglet.app.exit()
        if bool(parameter[0]) is True:
            controller = StartScreen(Events)
            controller.change_controller.subscribe(load_controller)
            pyglet.app.run(1/30)
    elif new_controller == "Statistics": controller = StatisticsScreen(Events, parameter, controller.__class__.__name__)  # gibt den Klassennamen mit, damit man zurück zum letzten Screen gehen kann)
    elif new_controller == "Settings": controller = SettingsScreen(Events, parameter, controller.__class__.__name__)  # gibt den Klassennamen mit, damit man zurück zum letzten Screen gehen kann
    elif new_controller == "HomeScreen": controller = HomeScreen(Events, parameter)
    elif new_controller == "StartScreen": controller = StartScreen(Events)
    elif new_controller == "DeleteSaveScreen": controller = DeleteSaveScreen(Events, parameter)
    else: controller = ErrorScreen(Events)

    # ermöglicht es, aus dem neuen Controller diese Methode aufzurufen
    controller.change_controller.subscribe(load_controller)
    controller.event.subscribe(decode_event)


def decode_event(data):
    event, *parameter = data  # entpackt data in die Einzelkomponenten

    if event == "ChangeColorScheme":
        logging.warning(parameter)
        Events.color_scheme = color_scheme.EditableColorScheme((parameter[0], parameter[1], parameter[2]))
        logging.warning(Events.color_scheme)


# setzt ersten Subscriptions
controller.change_controller.subscribe(load_controller)
controller.event.subscribe(decode_event)  # ermöglicht das Auslesen von Events aus dem aktuellen Screen

# startet das Spiel
pyglet.app.run(1/30)
