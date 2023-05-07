import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable


class MainLearningScreen:
    def __init__(self, events, save):
        save_file = save[0]
        self.batch = pyglet.graphics.Batch()
        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        background = pyglet.graphics.Group(order=-1)
        foreground = pyglet.graphics.Group(order=1)

        # Liste, die sämtliche subscriptions fängt, um sie beim Wechseln des Controllers wieder freizugeben
        sublist = []

        # Layout für den Startbildschirm des Lern-Modus
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, sublist, self.batch)
        self.header = ui_elements.BorderedRectangle("Lernen", 20, 75, 60, 20, events.color_scheme, color_scheme.Minecraft, 4, events, sublist, self.batch)

        self.back = ui_elements.InputButton("Zurück", 40, 10, 20, 10, events.color_scheme, color_scheme.Minecraft, 10, events, sublist, self.batch)
        self.settings = ui_elements.InputButton("Einstellungen", 2.5, 85, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 8, events, sublist, self.batch)
        self.statistics = ui_elements.InputButton("Statistiken", 85, 85, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 8.4, events, sublist, self.batch)

        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        sublist.extend((self.back.clicked.subscribe(lambda _: self.change_screen("HomeScreen", save_file)),
                        self.settings.clicked.subscribe(lambda _: self.change_screen("Settings", save_file)),
                        self.statistics.clicked.subscribe(lambda _: self.change_screen("Statistics", save_file))))

        self.disposable = CompositeDisposable(sublist)

        self.change_controller = Subject()
        self.event = Subject()  # separates Subject für eventuelle Events die in diesem Screen stattfinden

    def change_screen(self, new_screen, save):  # Wird getriggert, wenn man zurück zum Hauptmenü will
        # save suchen und auswählen
        self.change_controller.on_next((new_screen, save))

    def dispose_subs(self):  # Muss getriggert werden, wenn der Screen gewechselt wird.
        self.disposable.dispose()

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
