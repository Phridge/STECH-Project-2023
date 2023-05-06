import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable


class StartScreen:
    def __init__(self, events):
        self.batch = pyglet.graphics.Batch()
        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        background = pyglet.graphics.Group(order=-1)
        foreground= pyglet.graphics.Group(order=1)

        # Liste, die sämtliche subscriptions fängt, um sie beim Wechseln des Controllers wieder freizugeben
        sublist = []

        # Erstes Layout für den Hauptbildschirm
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, sublist, self.batch)
        self.header = ui_elements.BorderedRectangle("Die Maschinen-Revolution", 20, 75, 60, 20, events.color_scheme, color_scheme.Minecraft, 4.5, events, sublist, self.batch)
        self.save1 = ui_elements.InputButton("Erster Spielstand", 35, 55, 30, 10, events.color_scheme, color_scheme.Minecraft, 5.5, events, sublist, self.batch)
        self.save2 = ui_elements.InputButton("Zweiter Spielstand", 35, 42.5, 30, 10, events.color_scheme, color_scheme.Minecraft, 5.5, events, sublist, self.batch)
        self.save3 = ui_elements.InputButton("Dritter Spielstand", 35, 30, 30, 10, events.color_scheme, color_scheme.Minecraft, 5.5, events, sublist, self.batch)
        self.delete_save1 = ui_elements.InputButton("Neu 1", 67.5, 55, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 16, events, sublist, self.batch)
        self.delete_save2 = ui_elements.InputButton("Neu 2", 67.5, 42.5, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 16, events, sublist, self.batch)
        self.delete_save3 = ui_elements.InputButton("Neu 3", 67.5, 30, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 16, events, sublist, self.batch)
        self.info = ui_elements.BorderedRectangle("Hinweis: Gib mal \"Erster Spielstand\" auf der Tastatur ein!", 10, 12.5, 80, 10, events.color_scheme, color_scheme.Minecraft, 1.9, events, sublist, self.batch)
        self.settings = ui_elements.InputButton("Einstellungen", 2.5, 85, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 8, events, sublist, self.batch)
        self.statistics = ui_elements.InputButton("Statistiken", 85, 85, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 8.4, events, sublist, self.batch)

        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        sublist.extend((self.save1.clicked.subscribe(lambda _: self.save_clicked(1)),
                        self.save2.clicked.subscribe(lambda _: self.save_clicked(2)),
                        self.save3.clicked.subscribe(lambda _: self.save_clicked(3)),
                        self.delete_save1.clicked.subscribe(lambda _: self.new_save(1)),
                        self.delete_save2.clicked.subscribe(lambda _: self.new_save(2)),
                        self.delete_save3.clicked.subscribe(lambda _: self.new_save(3)),
                        self.settings.clicked.subscribe(lambda _: self.to_settings(0)),
                        self.statistics.clicked.subscribe(lambda _: self.to_statistics(0))))
        self.disposable = CompositeDisposable(sublist)

        self.change_controller = Subject()
        self.event = Subject()  # separates Subject für eventuelle Events die in diesem Screen stattfinden

    def save_clicked(self, data):  # Wird getriggert, wenn ein Spielstand ausgewählt wird
        # save suchen und auswählen
        self.change_controller.on_next(("HomeScreen", data))

    def new_save(self, data):  # fragt den Spieler noch einmal, ob der Spielstand wirklich gelöscht werden soll
        self.change_controller.on_next(("DeleteSaveScreen", data))

    def to_settings(self, data):
        self.change_controller.on_next(("Settings", data))

    def to_statistics(self, data):
        self.change_controller.on_next(("Statistics", data))

    def dispose_subs(self):  # Muss getriggert werden, wenn der Screen gewechselt wird.
        self.disposable.dispose()

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
