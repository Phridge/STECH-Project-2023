import logging
import time

import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable

"""
Eine Vorlage für einen Screen. ab Zeile 22 können Elemente eingefügt werde. Ein paar der ui-Elements sind als Beispiel gezeigt.
In dieser Datei sind nur die absoluten Essentials drin. Hinzufügen ist kein Problem, löschen schon.
Lasst euch dieses Template anzeigen, indem ihr es im main_controller als initialen Controller setzt :D
"""

class Level2Screen:
    def __init__(self, events):
        self.events = events
        self.batch = pyglet.graphics.Batch()
        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        background = pyglet.graphics.Group(order=-1)
        foreground = pyglet.graphics.Group(order=1)

        # Liste, die sämtliche subscriptions fängt, um sie beim Wechseln des Controllers wieder freizugeben
        self.sublist = []

        self.gif = ui_elements.Gif("assets/images/forest.gif", 0, 0, 100, 100, 30, True, self.events, self.sublist, self.batch, background)
        self.mech = ui_elements.GifButton("assets/images/mech_walk.gif", 30, 12, 13, 20, 0.75, True, self.events, self.sublist, self.batch)
        self.header = ui_elements.BorderedRectangle("Level 2: Der Wald des Widerstands", 20, 80, 60, 20, self.events.color_scheme, color_scheme.Minecraft, 2, self.events, self.sublist, self.batch)

        # Hier muss für jeden Button eine Subscription erstellt werden.
        # In der Lambda-Funktion wird dann die Funktion angebgeben, die aufgerufen werden soll wenn der jeweilige Button gedrückt wird
        self.sublist.append(self.mech.clicked.subscribe(lambda _: self.mech_hurt(True)))

        self.disposable = CompositeDisposable(self.sublist)

        self.change_controller = Subject()
        self.event = Subject()  # separates Subject für eventuelle Events die in diesem Screen stattfinden

    #  Falls die Funktionen namentlich nicht passen erstellte einfach neue!

    def mech_hurt(self, data):
        if data:
            logging.warning("AUA")
            self.mech.delete()
            self.mech = ui_elements.GifButton("assets/images/mech_hurt.gif", 30, 12, 13, 20, 0.25, True, self.events, self.sublist, self.batch)
            self.sublist.append(self.mech.loop_finished.subscribe(lambda _: self.mech_hurt(False)))
        else:
            self.mech.delete()
            self.mech = ui_elements.GifButton("assets/images/mech_walk.gif", 30, 12, 13, 20, 0.75, True, self.events, self.sublist, self.batch)
            self.sublist.append(self.mech.loop_finished.subscribe(lambda _: self.mech_hurt(False)))

    def button_clicked(self, data):  # Wird getriggert, wenn ein Spielstand ausgewählt wird
        self.change_controller.on_next(("HomeScreen", data))

    def dispose_subs(self):  # Muss getriggert werden, wenn der Screen gewechselt wird.
        self.disposable.dispose()

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
