import time

import pyglet
import pygame
import mixer
import contextlib
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex import just
from reactivex.operators import delay, scan, map as rmap, combine_latest, do_action, starmap
from reactivex.disposable import CompositeDisposable
from controller import Screen
from controller.actors import Player, ThePlayer
from ui_elements_ex import Rect, map_inner_perc


"""
Eine Vorlage für einen Screen. ab Zeile 22 können Elemente eingefügt werde. Ein paar der ui-Elements sind als Beispiel gezeigt.
In dieser Datei sind nur die absoluten Essentials drin. Hinzufügen ist kein Problem, löschen schon.
Lasst euch dieses Template anzeigen, indem ihr es im main_controller als initialen Controller setzt :D
"""


class Level1Screen(Screen):
    def __init__(self, events):
        super().__init__()
        self.events = events
        pos = events.size.pipe(
            rmap(lambda s: Rect(0, 0, *s))
        )
        self.batch = pyglet.graphics.Batch()
        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        background = pyglet.graphics.Group(order=-1)
        foreground = pyglet.graphics.Group(order=1)

        self.gif = ui_elements.Gif("assets/images/port.gif", 0, 0, 100, 100, 30, True, self.events, self.batch, background)

        # Player-Objekt
        # player = Player(self.events, self.batch, 20, 40, 20, 30)


        self.p = ThePlayer(running_speed=1.0, batch=self.batch, group=foreground)
        self._subs.add(events.update.pipe(
            scan(float.__add__, 0.0),
            combine_latest(
                pos.pipe(
                    map_inner_perc(0, 38, 100, 62),
                )
            ),
            starmap(lambda dt, pos: Rect(10 + 50 * dt, 10, 150, 150).offset(pos)),
        ).subscribe(self.p.pos))

        self.header = ui_elements.BorderedRectangle("Level 1: Der Hafen der Freiheit", 20, 80, 60, 20, self.events.color_scheme, color_scheme.Minecraft, 2, self.events, self.batch)

        self.change_controller = Subject()
        self.event = Subject()  # separates Subject für eventuelle Events die in diesem Screen stattfinden


    #  Falls die Funktionen namentlich nicht passen erstellte einfach neue!
    def button_clicked(self, data):  # Wird getriggert, wenn ein Spielstand ausgewählt wird
        self.change_controller.on_next(("HomeScreen", data))

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch

    def play_music(self, nextmusic):
        with contextlib.suppress(pygame.error):
            mixer.init()
            mixer.music.load(nextmusic)
            mixer.music.play()
            mixer.music.play(-1)