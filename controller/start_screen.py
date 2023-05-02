import logging
import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable


class StartScreen:
    def __init__(self, events):
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
                        self.delete_save1.clicked.subscribe(lambda _: self.delete_save(-1)),
                        self.delete_save2.clicked.subscribe(lambda _: self.delete_save(-2)),
                        self.delete_save3.clicked.subscribe(lambda _: self.delete_save(-3))))
        self.disposable = CompositeDisposable(sublist)

        self.change_controller = Subject()

    def save_clicked(self, data):  # Wird getriggert, wenn ein Spielstand ausgewählt wird
        # save suchen und auswählen
        logging.warning(("HomeScreen", data, "ist die neue Seite"))
        self.change_controller.on_next(("HomeScreen", data))

    def delete_save(self, data):  # Wird getriggert, wenn ein Spielstand gelöscht werden soll
        # datenbank stuff
        #  save löschen
        #  neuen erstellen
        pass

    def dispose_subs(self):  # Muss getriggert werden, wenn der Screen gewechselt wird.
        self.disposable.dispose()

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
