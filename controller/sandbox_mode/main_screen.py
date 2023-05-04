import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable


class MainSandboxScreen:
    def __init__(self, events, save):
        save = save[0]
        self.batch = pyglet.graphics.Batch()

        # Liste, die sämtliche subscriptions fängt, um sie beim Wechseln des Controllers wieder freizugeben
        sublist = []

        # Layout für den Startbildschirm des Sandbox-Modus
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, sublist, self.batch)
        self.header = ui_elements.BorderedRectangle("Sandbox", 20, 75, 60, 20, color_scheme.BlackWhite, color_scheme.Minecraft, 4, events, sublist, self.batch)

        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        '''sublist.extend((self.restart_button.clicked.subscribe(lambda _: self.button_clicked(True)),
                        self.end_button.clicked.subscribe(lambda _: self.button_clicked(False))))'''
        self.disposable = CompositeDisposable(sublist)

        self.change_controller = Subject()

    '''def button_clicked(self, data):  # Wird getriggert, wenn Buttons geklickt werden
            pass'''

    def dispose_subs(self):  # Muss getriggert werden, wenn der Screen gewechselt wird.
        self.disposable.dispose()

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
