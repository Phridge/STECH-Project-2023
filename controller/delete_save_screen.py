import logging

import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable

class DeleteSaveScreen:
    def __init__(self, events, save):
        save = save[0]
        self.batch = pyglet.graphics.Batch()

        # Liste, die sämtliche subscriptions fängt, um sie beim Wechseln des Controllers wieder freizugeben
        sublist = []

        # Design
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, sublist, self.batch)
        self.header = ui_elements.BorderedRectangle("Spielstand " + str(save) + " wirklich löschen?", 20, 75, 60, 20, events.color_scheme, color_scheme.Minecraft, 3.4, events, sublist, self.batch)
        self.button1 = ui_elements.InputButton("Ja", 30, 55, 17.5, 10, events.color_scheme, color_scheme.Minecraft, 16, events, sublist, self.batch)
        self.button2 = ui_elements.InputButton("Nein", 52.5, 55, 17.5, 10, events.color_scheme, color_scheme.Minecraft, 16, events, sublist, self.batch)

        # erstellt Sublist, damit der Screen vollständig verworfen wird
        sublist.extend((self.button1.clicked.subscribe(lambda _: self.delete_save(save)),
                        self.button2.clicked.subscribe(lambda _: self.back_to_menu(0))))

        self.disposable = CompositeDisposable(sublist)
        self.change_controller = Subject()
        self.event = Subject()  # separates Subject für eventuelle Events die in diesem Screen stattfinden

    def delete_save(self, data):  # Wird getriggert, wenn ein Spielstand ausgewählt wird
        # Hier muss der Save gelöscht werden
        logging.warning("SAVE WIRD NOCH NICHT GELÖSCHT")
        self.change_controller.on_next(("StartScreen", data))

    def back_to_menu(self, data):  # Wird getriggert, wenn ein Spielstand ausgewählt wird
        self.change_controller.on_next(("StartScreen", data))

    def dispose_subs(self):  # Muss getriggert werden, wenn der Screen gewechselt wird.
        self.disposable.dispose()

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
