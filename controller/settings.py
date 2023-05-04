import logging

import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable


class SettingsScreen:
    def __init__(self, events, save, previous_controller):
        save = save[0]
        self.batch = pyglet.graphics.Batch()

        # Liste, die sämtliche subscriptions fängt, um sie beim Wechseln des Controllers wieder freizugeben
        sublist = []

        # Layout für den Einstellungs-Bildschirm
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, sublist, self.batch)
        self.header = ui_elements.BorderedRectangle("Einstellungen", 20, 75, 60, 20, color_scheme.BlackWhite, color_scheme.Minecraft, 4, events, sublist, self.batch)
        self.back = ui_elements.InputButton("Zurück", 20, 62.5, 60, 10, color_scheme.BlackWhite, color_scheme.Minecraft, 4, events, sublist, self.batch)
        self.color_picker_red = ui_elements.TextField(3, 20, 50, 17.5, 10, color_scheme.BlackWhite, color_scheme.Minecraft, 4, events, sublist, "red", self.batch)
        self.color_picker_green = ui_elements.TextField(3, 41.25, 50, 17.5, 10, color_scheme.BlackWhite, color_scheme.Minecraft, 4, events, sublist, "green", self.batch)
        self.color_picker_blue = ui_elements.TextField(3, 62.5, 50, 17.5, 10, color_scheme.BlackWhite, color_scheme.Minecraft, 4, events, sublist, "blue", self.batch)


        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        sublist.extend((self.back.clicked.subscribe(lambda _: self.go_back(previous_controller, save)),
                        self.color_picker_red.changed.subscribe(self.change_color),
                        self.color_picker_red.clicked.subscribe(lambda _: self.button_active("red")),
                        self.color_picker_green.changed.subscribe(self.change_color),
                        self.color_picker_green.clicked.subscribe(lambda _: self.button_active("green")),
                        self.color_picker_blue.changed.subscribe(self.change_color),
                        self.color_picker_blue.clicked.subscribe(lambda _: self.button_active("blue"))))
        self.disposable = CompositeDisposable(sublist)

        self.change_controller = Subject()
        self.event = Subject()  # separates Subject für eventuelle Events die in diesem Screen stattfinden

    def go_back(self, previous_controller, save):  # Wird getriggert, wenn Buttons geklickt werden
        self.change_controller.on_next((previous_controller, save))

    def change_color(self, data):
        if self.color_picker_red.text.isnumeric(): red = int(self.color_picker_red.text)
        else: red = 0
        if self.color_picker_green.text.isnumeric(): green = int(self.color_picker_green.text)
        else: green = 0
        if self.color_picker_blue.text.isnumeric(): blue = int(self.color_picker_blue.text)
        else: blue = 0
        self.event.on_next(("ChangeColorScheme", red, green, blue))

    def button_active(self, data):
        self.color_picker_red.set_active(True if data == "red" else False)
        self.color_picker_green.set_active(True if data == "green" else False)
        self.color_picker_blue.set_active(True if data == "blue" else False)

    def dispose_subs(self):  # Muss getriggert werden, wenn der Screen gewechselt wird.
        self.disposable.dispose()

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
