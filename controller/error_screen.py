import logging
import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable


class ErrorScreen:
    def __init__(self, events):
        self.batch = pyglet.graphics.Batch()

        # Liste, die sämtliche subscriptions fängt, um sie beim Wechseln des Controllers wieder freizugeben
        sublist = []

        # Erstes Layout für den Error-Bildschirm
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, sublist, self.batch)
        self.gif = ui_elements.Gif("assets/images/popcat.gif", 30, 10, 40, 40, 0.5, True, events, sublist, self.batch)
        self.Header = ui_elements.BorderedRectangle("Es liegt ein Fehler vor :(", 20, 75, 60, 20, color_scheme.BlackWhite, color_scheme.Minecraft, 5, events, sublist, self.batch)
        self.save1 = ui_elements.BorderedRectangleButton("Zurück zum Hauptmenü", 35, 55, 30, 10, color_scheme.BlackWhite, color_scheme.Minecraft, 6, events, sublist, self.batch)

        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        sublist.append(self.save1.clicked.subscribe(lambda _: self.restart(1)))
        self.disposable = CompositeDisposable(sublist)

        self.change_controller = Subject()

    def restart(self, data):  # Wird getriggert, wenn ein Spielstand ausgewählt wird
        # save suchen und auswählen
        logging.warning(("StartScreen", data))
        self.change_controller.on_next(("StartScreen", data))

    def dispose_subs(self):  # Muss getriggert werden, wenn der Screen gewechselt wird.
        self.disposable.dispose()

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
