import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable

from controller import Screen
from controller.start_screen import StartScreen

"""
Eine Vorlage für einen Screen. ab Zeile 22 können Elemente eingefügt werde. Ein paar der ui-Elements sind als Beispiel gezeigt.
In dieser Datei sind nur die absoluten Essentials drin. Hinzufügen ist kein Problem, löschen schon.
Lasst euch dieses Template anzeigen, indem ihr es im main_controller als initialen Controller setzt :D
"""


class StoryLevelScreen(Screen):
    def __init__(self, events):
        super().__init__()
        self.batch = pyglet.graphics.Batch()

        # im folgenden Block können Elemente eingefügt werden. Die Elemente die schon da sind dienen nur als Beispiele
        # self.gif = ui_elements.Gif("assets/images/bridge.gif", 0, 0, 100, 100, 2, True, events, sublist, self.batch)
        self.gif = ui_elements.Gif("assets/images/mech_walk_1.gif", 40, 40, 24, 40, 1, True, events, self.batch)
        self.Header = ui_elements.BorderedRectangle("Level 3", 35, 90, 30, 10, color_scheme.BlackWhite, color_scheme.Minecraft, 5, events, self.batch)
        self.Header = ui_elements.BorderedRectangle("Die dampfbetriebene Brücke", 35, 85, 30, 10, color_scheme.BlackWhite, color_scheme.Minecraft, 4, events, self.batch)
        self.button = ui_elements.BorderedRectangleButton("Button", 25, 85, 30, 10, color_scheme.BlackWhite, color_scheme.Minecraft, 4, events, self.batch)

        # Hier muss für jeden Button eine Subscription erstellt werden.
        # In der Lambda-Funktion wird dann die Funktion angebgeben, die aufgerufen werden soll wenn der jeweilige Button gedrückt wird
        self.button.clicked.subscribe(lambda _: self.go_to(StartScreen))

    #  Falls die Funktionen namentlich nicht passen erstellte einfach neue!
    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
