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
from controller.story_mode.level1_screen import Level1Screen
from controller.story_mode.level2_screen import Level2Screen
from controller.story_mode.level3_screen import Level3Screen
from controller.story_mode.main_screen import MainStoryScreen
from controller.learning_mode.main_screen import MainLearningScreen
from controller.sandbox_mode.main_screen import MainSandboxScreen

# Beispiel-Bildschirm
from controller.template_screen import TemplateScreen

window = pyglet.window.Window(resizable=False)


class Events:
    key = Subject()
    text = Subject()
    mouse = BehaviorSubject((0, 0, 0))
    mouse_move = Subject()
    mouse_button = Subject()
    size = BehaviorSubject((window.width, window.height))  # Sollte hier eigentlich aus der Datenbank(DB) gelesen werden
    color_scheme = color_scheme.BlackWhite  # Sollte hier eigentlich aus der Datenbank(DB) gelesen werden
    volume_value = 0  # Sollte hier eigentlich aus der Datenbank(DB) gelesen werden
    fullscreen = False  # Sollte hier eigentlich aus der Datenbank(DB) gelesen werden


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

logging.warning("Oben bei Events muss das Color_scheme aus der Datenbank importiert werden")
controller = Level3Screen(Events)  # Setzt StartBildschirm als initialen Controller
sublist = []  # erstellte eine sublist, die ermöglicht Subscriptions wieder aufzuheben


def load_controller(data):
    """
    Wird aufgerufen, wenn ein Controller zu einem anderen Controller wechseln will. Trennt auch alle Subscriptions zum alten Controller.

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
    if new_controller == "Restart":  # Handelt Rückgabe des ErrorScreens
        pyglet.app.exit()
        if bool(parameter[0]) is True:
            controller = StartScreen(Events)
            controller.change_controller.subscribe(load_controller)
            pyglet.app.run(1/30)
    elif new_controller == "Statistics": controller = StatisticsScreen(Events, controller.__class__.__name__, parameter)  # gibt den Klassennamen mit, damit man zurück zum letzten Screen gehen kann)
    elif new_controller == "Settings": controller = SettingsScreen(Events, controller.__class__.__name__, parameter)  # gibt den Klassennamen mit, damit man zurück zum letzten Screen gehen kann
    elif new_controller == "ReloadSettings": controller = SettingsScreen(Events, parameter[0], parameter[1])  # gibt den Klassennamen mit, damit man zurück zum letzten Screen gehen kann
    elif new_controller == "HomeScreen": controller = HomeScreen(Events, parameter)
    elif new_controller == "StartScreen": controller = StartScreen(Events)
    elif new_controller == "DeleteSaveScreen": controller = DeleteSaveScreen(Events, parameter)
    elif new_controller == "MainLearningScreen": controller = MainLearningScreen(Events, parameter)
    elif new_controller == "MainStoryScreen": controller = MainStoryScreen(Events, parameter)
    elif new_controller == "MainSandboxScreen": controller = MainSandboxScreen(Events, parameter)
    else: controller = ErrorScreen(Events)  # falls auf eine nicht existente Seite verwiesen wird, wird ein Error-Screen aufgerufen

    # ermöglicht es, aus dem neuen Controller diese Methode aufzurufen
    sublist.append(controller.change_controller.subscribe(load_controller))
    sublist.append(controller.event.subscribe(decode_event))


def decode_event(data):
    """
    Wird aufgerufen falls Screens ein Event haben, was zurückgegeben wird (außer Screen-Wechsel)

    :param data: Name des Events als String, und Parameter als ein Tupel (event, *parameter)
    """
    event, *parameter = data  # entpackt data in die Einzelkomponenten

    if event == "ChangeColorScheme":  # ändert das Farbschema des gesamten Spiels. Parameter beinhaltet das fertige ColorScheme
        logging.warning("HIER SOLLTE DAS FARBSCHEMA IN DIE DATENBANK(DB) GESPEICHERT WERDEN")
        Events.color_scheme = parameter[0]
    elif event == "ChangeVolume":  # ändert das Farbschema des gesamten Spiels. Parameter beinhaltet das fertige ColorScheme
        logging.warning("HIER SOLLTE DAS VOLUME IN DIE DATENBANK(DB) GESPEICHERT WERDEN")
        Events.volume_value = parameter[0]
    elif event == "ToggleFullscreen":  # togglet Vollbild an und aus
        logging.warning("HIER SOLLTE DAS Fullscreen-Value IN DIE DATENBANK(DB) GESPEICHERT WERDEN")
        if parameter[0] is True:
            Events.fullscreen = False
            window.set_fullscreen(False)
        else:
            Events.fullscreen = True
            window.set_fullscreen(True)
    elif event == "ChangeScreenSize": # änddert die Größe des Bildschirms
        logging.warning("HIER SOLLTE Die FENSTERGRÖßE IN DIE DATENBANK(DB) GESPEICHERT WERDEN")
        window.set_size(int(parameter[0]), int(parameter[1]))


# setzt ersten Subscriptions
sublist.append(controller.change_controller.subscribe(load_controller))
sublist.append(controller.event.subscribe(decode_event))  # ermöglicht das Auslesen von Events aus dem aktuellen Screen

# startet das Spiel
pyglet.app.run(1/30)
