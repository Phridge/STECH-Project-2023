import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable


class StatisticsScreen:
    def __init__(self, events, previous_controller, save):
        save = save[0]
        if save == 0: save_text = "Alle Spielstände"
        else: save_text = "Spielstand " + str(save)

        self.batch = pyglet.graphics.Batch()

        # Liste, die sämtliche subscriptions fängt, um sie beim Wechseln des Controllers wieder freizugeben
        sublist = []

        # Layout für den Statistik-Bildschirm
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, sublist, self.batch)
        self.header = ui_elements.BorderedRectangle("Statistiken", 20, 75, 60, 20, events.color_scheme, color_scheme.Minecraft, 4, events, sublist, self.batch)
        self.current_stats = ui_elements.BorderedRectangle(save_text, 20, 62.5, 60, 10, events.color_scheme, color_scheme.Minecraft, 4, events, sublist, self.batch)
        self.back = ui_elements.InputButton("Zurück", 20, 50, 60, 10, events.color_scheme, color_scheme.Minecraft,
                                            4, events, sublist, self.batch)

        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        sublist.append(self.back.clicked.subscribe(lambda _: self.go_back(previous_controller, save)))
        self.disposable = CompositeDisposable(sublist)

        self.change_controller = Subject()
        self.event = Subject()  # separates Subject für eventuelle Events die in diesem Screen stattfinden

    def go_back(self, previous_controller, save):  # Wird getriggert, wenn Buttons geklickt werden
        self.change_controller.on_next((previous_controller, save))

    def dispose_subs(self):  # Muss getriggert werden, wenn der Screen gewechselt wird.
        self.disposable.dispose()

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
