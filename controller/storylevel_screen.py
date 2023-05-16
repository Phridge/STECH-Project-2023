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


class StoryLevelScreen:
    def __init__(self, events):
        self.batch = pyglet.graphics.Batch()

        # Liste, die sämtliche subscriptions fängt, um sie beim Wechseln des Controllers wieder freizugeben
        sublist = []

        # im folgenden Block können Elemente eingefügt werden. Die Elemente die schon da sind dienen nur als Beispiele
        # self.gif = ui_elements.Gif("assets/images/bridge.gif", 0, 0, 100, 100, 2, True, events, sublist, self.batch)
        self.gif = ui_elements.Gif("assets/images/mech_walk_1.gif", 40, 40, 24, 40, 1, True, events, sublist, self.batch)
        self.Header = ui_elements.BorderedRectangle("Level 3", 35, 90, 30, 10, color_scheme.BlackWhite, color_scheme.Minecraft, 5, events, sublist, self.batch)
        self.Header = ui_elements.BorderedRectangle("Die dampfbetriebene Brücke", 35, 85, 30, 10, color_scheme.BlackWhite, color_scheme.Minecraft, 4, events, sublist, self.batch)

        # Hier muss für jeden Button eine Subscription erstellt werden.
        # In der Lambda-Funktion wird dann die Funktion angebgeben, die aufgerufen werden soll wenn der jeweilige Button gedrückt wird
        #sublist.extend((self.button1.clicked.subscribe(lambda _: self.button_clicked(1)),
        #                self.button2.clicked.subscribe(lambda _: self.button_clicked(2)),
        #                self.button3.clicked.subscribe(lambda _: self.button_clicked(3))))

        self.disposable = CompositeDisposable(sublist)
        self.change_controller = Subject()

    #  Falls die Funktionen namentlich nicht passen erstellte einfach neue!
    def button_clicked(self, data):  # Wird getriggert, wenn ein Spielstand ausgewählt wird
        self.change_controller.on_next(("HomeScreen", data))

    def dispose_subs(self):  # Muss getriggert werden, wenn der Screen gewechselt wird.
        self.disposable.dispose()

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
