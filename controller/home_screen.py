import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable


class HomeScreen:
    def __init__(self, events, save_file):
        save_file = save_file[0]
        self.batch = pyglet.graphics.Batch()

        # Liste, die sämtliche subscriptions fängt, um sie beim Wechseln des Controllers wieder freizugeben
        sublist = []

        # Erstes Layout für den HomeScreen
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, sublist, self.batch)
        self.Header = ui_elements.BorderedRectangle("HomeScreen von Save " + str(save_file), 20, 75, 60, 20, color_scheme.BlackWhite, color_scheme.Minecraft, 5, events, sublist, self.batch)
        self.back = ui_elements.InputButton("Zurück", 35, 55, 30, 10, color_scheme.BlackWhite, color_scheme.Minecraft, 6, events, sublist, self.batch)
        self.to_error = ui_elements.InputButton("auf nicht existente Seite wechseln (versuchen)", 25, 42.5, 50, 10, color_scheme.BlackWhite, color_scheme.Minecraft, 2.3, events, sublist, self.batch)

        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        sublist.extend((self.back.clicked.subscribe(lambda _: self.go_back(1)),
                        self.to_error.clicked.subscribe(lambda _: self.go_to_error(2))))
        self.disposable = CompositeDisposable(sublist)

        self.change_controller = Subject()

    def go_back(self, data):  # Wird getriggert, wenn man zurück zum Hauptmenü will
        # save suchen und auswählen
        self.change_controller.on_next(("StartScreen", data))

    def go_to_error(self, data):  # verweist auf eine nicht existente Seite --> routet zur Error-Page
        self.change_controller.on_next(("NichtExistenteSeite", 0))

    def dispose_subs(self):  # Muss getriggert werden, wenn der Screen gewechselt wird.
        self.disposable.dispose()

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
