import logging as l
l.basicConfig(filename="log.log", level=l.DEBUG)

from contextlib import suppress
from dataclasses import dataclass
from sys import stdout
from typing import Any, Callable, Optional

import pygame
from pygame import mixer
import pyglet
import pygame
import reactivex
from reactivex import Observer
from reactivex.subject import BehaviorSubject, Subject
from reactivex.disposable import CompositeDisposable, MultipleAssignmentDisposable, SerialDisposable
import color_scheme
from controller import Screen
from controller.start_screen import StartScreen
from events import Events, Event, Var, Disposable
from tools import save_and_open

ScreenInit = Callable[[Events], Screen]


@dataclass
class SwitchScreen:
    """Befehl für main_controller.switch_screen."""
    screen_init: ScreenInit


@dataclass
class ReloadScreen:
    """Befehl für main_controller.reload_screen."""
    screen_init: ScreenInit | None = None


@dataclass
class PushScreen:
    """Befehl für main_controller.push_screen."""
    screen_init: ScreenInit


@dataclass
class PopScreen:
    """Befehl für main_controller.pop_screen."""
    pass


@dataclass
class Exit:
    restart: bool = False


@dataclass
class SetFullscreen:
    state: bool


@dataclass
class ChangeSetting:
    setting: str
    value: Any


class GameWindow(pyglet.window.Window, Disposable):
    def __init__(self):
        super().__init__(resizable=False, caption="Typerpunk")
        self.events = Events(
            key=Event(),
            text=Event(),
            mouse=Var((0, 0, 0)),
            mouse_move=Event(),
            mouse_button=Event(),
            update=Event(),
            size=Var((self.width, self.height)),
            color_scheme=color_scheme.BlackWhite,
            volume=Var(0.5),
            fullscreen=False,   
        )

        # Updated die Settings aus der Datenbank
        settings = save_and_open.get_settings(0)
        self.events.color_scheme = settings[2]
        self.events.volume.on_next(settings[1])
        self.events.fullscreen = settings[0]
        self.set_fullscreen(self.events.fullscreen)
        if settings[3] and not self.events.fullscreen:
            self._handle_command(ChangeSetting("size", settings[3]))

        with suppress(pygame.error):
            mixer.init()
        self.volume_sub = self.events.volume.subscribe(mixer.music.set_volume, on_error=lambda e: None)

        self.history = []

        self.controller = None

        self.controller_subs = SerialDisposable()

        # self.push_screen(Level1Screen)
        self.push_screen(StartScreen)
        self.set_icon(pyglet.image.load("assets/images/icon.png"))


    def push_screen(self, screen_init):
        """
        Wechselt zum angegebenen Screen und behält alle bisherigen Screens in der Historie bei.

        In der Historie kann danach bspw. mit main_controller.pop_screen zurückgesprungen werden
        """
        self.history.append(screen_init)
        self.controller = screen_init(self.events)
        self._reset_subs()

    def reload_screen(self, screen_init=None):
        """
        Lädt den aktuell Screen neu oder ersetzt den aktuellen durch einen neuen.
        """
        old = self.history.pop()
        screen_init = screen_init or old
        self.push_screen(screen_init)

    def switch_screen(self, screen_init):
        """
        Wechselt zum angegebenen Screen und LÖSCHT DIE HISTORIE.

        Nach solch einem Befehl ist kein pop_screen() möglich.
        """
        self.history.clear()
        self.push_screen(screen_init)

    def pop_screen(self):
        """Geht einen Screen in der Historie zurück (lädt den vorangegangen Screen)"""
        self.history.pop()
        self.push_screen(self.history.pop())

    def _reset_subs(self):
        """Setzt alle Subscriptions zurück"""
        self.controller_subs.disposable = CompositeDisposable([
            self.controller.game_command.subscribe(self._handle_command),
            self.controller,
        ])

    def _handle_command(self, cmd):
        """
        Behandelt eingehende Befehle zur Navigation der verschiedenen Screens
        :param cmd: Art von Navigation, die getätigt werden soll
        """
        match cmd:
            case SwitchScreen(screen_init):
                self.switch_screen(screen_init)
            case PushScreen(screen_init):
                self.push_screen(screen_init)
            case ReloadScreen(screen_init):
                self.reload_screen(screen_init)
            case PopScreen():
                self.pop_screen()
            case SetFullscreen(state=fullscreen):
                self.events.fullscreen = fullscreen
                self.set_fullscreen(fullscreen)
            case ChangeSetting(name, value):
                match name:
                    case "volume": self.events.volume.on_next(value)
                    case "size": self.set_size(*value)
                    case "color_scheme": self.events.color_scheme = value
            case Exit(restart):
                if restart:
                    try:
                        pyglet.app.exit()
                    except Exception:
                        pass
                else:
                    try:
                        pyglet.app.exit()
                    except Exception:
                        pass

    def on_draw(self, *args):
        """
        Wird aufgerufen, wenn das Hauptfenster gerendert wird
        :param args: ergänzen
        """
        self.clear()
        view = self.controller.get_view()
        view.draw()

    def on_key_press(self, keycode, mods):
        """
        Leitet alle getätigten Tastendrucke weiter
        :param keycode: Keycode der Taste, die gedrückt wurde
        :param mods: ergänzen
        """
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
        super().on_resize(w, h)
        self.events.size.on_next((w, h))

    def on_refresh(self, dt):
        self.events.update.on_next(dt)


def main():
    window = GameWindow()
    l.debug("WORKS")

    # startet das Spiel
    pyglet.app.run(1/30)





if __name__ == "__main__":
    print("bitte main.py laufen lassen! danke")
    exit(1)
