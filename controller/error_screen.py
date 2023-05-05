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
        # self.gif = ui_elements.Gif("assets/images/popcat.gif", 30, 10, 40, 40, 0.5, True, events, sublist, self.batch)
        self.header = ui_elements.BorderedRectangle("Es liegt ein Fehler vor :(", 20, 75, 60, 20, events.color_scheme, color_scheme.Minecraft, 4, events, sublist, self.batch)
        self.restart_button = ui_elements.InputButton("Neu Starten", 35, 55, 30, 10, events.color_scheme, color_scheme.Minecraft, 6, events, sublist, self.batch)
        self.end_button = ui_elements.InputButton("Spiel beenden", 35, 37.5, 30, 10, events.color_scheme, color_scheme.Minecraft, 6, events, sublist, self.batch)

        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        sublist.extend((self.restart_button.clicked.subscribe(lambda _: self.restart(True)),
                        self.end_button.clicked.subscribe(lambda _: self.restart(False))))
        self.disposable = CompositeDisposable(sublist)

        self.change_controller = Subject()
        self.event = Subject()  # separates Subject für eventuelle Events die in diesem Screen stattfinden

    def restart(self, data):  # Wird getriggert, wenn ein Spielstand ausgewählt wird
        self.change_controller.on_next(("Restart", data))

    def dispose_subs(self):  # Muss getriggert werden, wenn der Screen gewechselt wird.
        self.disposable.dispose()

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch