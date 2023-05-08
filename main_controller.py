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
from controller.story_mode.level2_screen import Level2Screen
from controller.story_mode.main_screen import MainStoryScreen
from controller.learning_mode.main_screen import MainLearningScreen
from controller.sandbox_mode.main_screen import MainSandboxScreen

# Beispiel-Bildschirm
from controller.template_screen import TemplateScreen
from events import Events, Event, Var, Disposable


class GameWindow(pyglet.window.Window, Disposable):
    def __init__(self):
        super().__init__(resizable=False)
        self.events = Events(
            key=Event(),
            text=Event(),
            mouse=Var((0, 0, 0)),
            mouse_move=Event(),
            mouse_button=Event(),
            size=Var((self.width, self.height)),
            color_scheme=color_scheme.BlackWhite,
            volume=0,
            fullscreen=False,
        )

        self.controller = StartScreen(self.events)


        self.controller_subs = CompositeDisposable([
            self.controller.change_controller.subscribe(self.load_controller),
            self.controller.event.subscribe(self.decode_event)  # ermöglicht das Auslesen von Events aus dem aktuellen Screen
        ])

        self.sublist = []


    def load_controller(self, data):
        """
        Wird aufgerufen, wenn ein Controller zu einem anderen Controller wechseln will. Trennt auch alle Subscriptions zum alten Controller.

        :param data: der Name des neuen Controllers als string, und eventuell ein parameter (new_controller, *parameter)
        """

        # löscht alle subscriptions im main_controller
        CompositeDisposable(self.sublist).dispose()
        self.sublist = []  # leert die sublist


        # löscht die subscriptions des alten Controllers und den controller selbst.
        self.controller_subs.dispose()
        self.controller_subs = None

        # jetzt ist erstmal aufgeräumt.

        # matchen, was gemacht werden soll
        match data:
            case ("Restart", restart):  # Handelt Rückgabe des ErrorScreens
                if restart:
                    self.controller = StartScreen(self.events)
                else:
                    pyglet.app.exit()
            case ("Statistics", save):
                self.controller = StatisticsScreen(self.events, self.controller.__class__.__name__, save)
            case ("Settings", save):
                self.controller = SettingsScreen(self.events, self.controller.__class__.__name__, save)  # gibt den Klassennamen mit, damit man zurück zum letzten Screen gehen kann
            case ("ReloadSettings", prev_controller, save):
                self.controller = SettingsScreen(self.events, prev_controller, save)  # gibt den Klassennamen mit, damit man zurück zum letzten Screen gehen kann
            case ("HomeScreen", save):
                self.controller = HomeScreen(self.events, save)
            case ("StartScreen", save):
                self.controller = StartScreen(self.events)
            case ("DeleteSaveScreen", save):
                self.controller = DeleteSaveScreen(self.events, save)
            case ("MainLearningScreen", save):
                self.controller = MainLearningScreen(self.events, save)
            case ("MainStoryScreen", save):
                self.controller = MainStoryScreen(self.events, save)
            case ("MainSandboxScreen", save):
                self.controller = MainSandboxScreen(self.events, save)
            case other:
                print(other)
                self.controller = ErrorScreen(self.events)  # falls auf eine nicht existente Seite verwiesen wird, wird ein Error-Screen aufgerufen


        self.controller_subs = CompositeDisposable([
            self.controller.change_controller.subscribe(self.load_controller),
            self.controller.event.subscribe(self.decode_event)  # ermöglicht das Auslesen von Events aus dem aktuellen Screen
        ])


    def decode_event(self, data):
        """
        Wird aufgerufen falls Screens ein Event haben, was zurückgegeben wird (außer Screen-Wechsel)

        :param data: Name des Events als String, und Parameter als ein Tupel (event, *parameter)
        """

        match data:
            case ("ChangeColorScheme", c):
                self.events.color_scheme = c
            case ("ChangeVolume", volume):
                self.events.volume = volume
            case ("ToggleFullscreen", fullscreen):
                self.set_fullscreen(fullscreen)
                self.events.fullscreen = fullscreen
            case ("ChangeScreenSize", int(w), int(h)):
                self.set_size(w, h)
                self.events.size.on_next((w, h))


    def on_draw(self, *args):
        self.clear()
        view = self.controller.get_view()
        view.draw()

    def on_key_press(self, keycode, mods):
        self.events.key.on_next((keycode, mods))

    def on_text(self, text):
        self.events.text.on_next(text)

    def on_mouse_motion(self, x, y, dx, dy):
        self.events.mouse_move.on_next((x, y, dx, dy))
        self.events.mouse.on_next((x, y, False))

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.events.mouse_move.on_next((x, y, dx, dy))
        self.events.mouse.on_next((x, y, buttons))

    def on_mouse_press(self, x, y, button, modifiers):
        self.events.mouse_button.on_next((True, x, y, button))

    def on_mouse_release(self, x, y, button, modifiers):
        self.events.mouse_button.on_next((False, x, y, button))

    def on_resize(self, w, h):
        self.events.size.on_next((w, h))


def main():
    window = GameWindow()

    # startet das Spiel
    pyglet.app.run(1/30)

    window.dispose()


if __name__ == "__main__":
    main()
