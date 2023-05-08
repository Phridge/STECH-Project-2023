import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable

from controller import Screen


class PauseScreen(Screen):
    def __init__(self, events, save):
        super().__init__()

        self.batch = pyglet.graphics.Batch()
        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        background = pyglet.graphics.Group(order=-1)
        foreground = pyglet.graphics.Group(order=1)

        # Layout für den Pause-Bildschirm
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, self.batch)
        self.header = ui_elements.BorderedRectangle("Pause", 20, 75, 60, 20, events.color_scheme, color_scheme.Minecraft, 4, events, self.batch)

        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        '''sublist.extend((self.restart_button.clicked.subscribe(lambda _: self.button_clicked(True)),
                        self.end_button.clicked.subscribe(lambda _: self.button_clicked(False))))'''

        self.change_controller = Subject()
        self.event = Subject()  # separates Subject für eventuelle Events die in diesem Screen stattfinden

    '''def button_clicked(self, data):  # Wird getriggert, wenn Buttons geklickt werden
            pass'''

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
