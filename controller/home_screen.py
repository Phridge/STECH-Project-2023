import logging
import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable


class Controller:
    def get_view(self):
        raise NotImplementedError


class HomeScreen(Controller):
    def __init__(self, events, save_file):
        save_file = save_file[0]
        self.batch = pyglet.graphics.Batch()

        # Liste, die sämtliche subscriptions fängt, um sie beim Wechseln des Controllers wieder freizugeben
        sublist = []

        # Erstes Layout für den HomeScreen
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, sublist, self.batch)
        self.Header = ui_elements.BorderedRectangle("HomeScreen von Save " + str(save_file), 20, 75, 60, 20, color_scheme.BlackWhite, color_scheme.Minecraft, 5, events, sublist, self.batch)
        self.save1 = ui_elements.BorderedRectangleButton("Zurück", 35, 55, 30, 10, color_scheme.BlackWhite, color_scheme.Minecraft, 6, events, sublist, self.batch)
        self.save2 = ui_elements.BorderedRectangleButton("auf nicht existente Seite wechseln (versuchen)", 25, 42.5, 50, 10, color_scheme.BlackWhite, color_scheme.Minecraft, 3, events, sublist, self.batch)

        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        sublist.extend((self.save1.clicked.subscribe(lambda _: self.save_clicked(1)),
                        self.save2.clicked.subscribe(lambda _: self.delete_save(2))))
        self.disposable = CompositeDisposable(sublist)

        self.change_controller = Subject()

    def save_clicked(self, data):  # Wird getriggert, wenn ein Spielstand ausgewählt wird
        # save suchen und auswählen
        logging.warning(("StartScreen", data))
        self.change_controller.on_next(("StartScreen", data))

    def delete_save(self, data):  # Wird getriggert, wenn ein Spielstand gelöscht werden soll
        # datenbank stuff
        #  save löschen
        #  neuen erstellen
        self.change_controller.on_next("save")
        logging.warning(("Deleting Save", data))

    def dispose_subs(self):  # Muss getriggert werden, wenn der Screen gewechselt wird.
        self.disposable.dispose()

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
