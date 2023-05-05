import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable


class SettingsScreen:
    def __init__(self, events, save, previous_controller):
        save = save[0]
        self.batch = pyglet.graphics.Batch()
        self.preview_color_scheme = events.color_scheme

        # Liste, die sämtliche subscriptions fängt, um sie beim Wechseln des Controllers wieder freizugeben
        sublist = []

        # Layout für den Einstellungs-Bildschirm
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, sublist, self.batch)
        self.header = ui_elements.BorderedRectangle("Einstellungen", 20, 75, 60, 20, events.color_scheme, color_scheme.Minecraft, 4, events, sublist, self.batch)
        self.back = ui_elements.InputButton("Zurück", 20, 62.5, 60, 10, events.color_scheme, color_scheme.Minecraft, 4, events, sublist, self.batch)
        self.color_picker_red = ui_elements.SettingTextField(3, 255, 20, 50, 17.5, 10, color_scheme.EditableColorScheme((255, 0, 0)), color_scheme.Minecraft, 9, events, sublist, "red", self.batch)
        self.color_picker_green = ui_elements.SettingTextField(3, 255, 41.25, 50, 17.5, 10, color_scheme.EditableColorScheme((0, 255, 0)), color_scheme.Minecraft, 9, events, sublist, "green", self.batch)
        self.color_picker_blue = ui_elements.SettingTextField(3, 255, 62.5, 50, 17.5, 10, color_scheme.EditableColorScheme((0, 0, 255)), color_scheme.Minecraft, 9, events, sublist, "blue", self.batch)
        self.color_preview = ui_elements.BorderedRectangle("Beispiel", 83.75, 50, 10, 10, self.preview_color_scheme, color_scheme.Minecraft, 10, events, sublist, self.batch)


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

    def go_back(self, previous_controller, save):
        """
        Routet zurück zum letzten Controller

        :param previous_controller: Name des letzten Controllers --> Wechsel-Ziel
        :param save: aktuelle Save-File
        """
        self.event.on_next(("ChangeColorScheme", self.preview_color_scheme))
        self.change_controller.on_next((previous_controller, save))

    def change_color(self, data):
        """
        Ändert das Farbschema des gesamten Spiels und aktualisiert die Preview-Box
        """
        if self.color_picker_red.text.isnumeric(): red = int(self.color_picker_red.text)
        else: red = 0
        if self.color_picker_green.text.isnumeric(): green = int(self.color_picker_green.text)
        else: green = 0
        if self.color_picker_blue.text.isnumeric(): blue = int(self.color_picker_blue.text)
        else: blue = 0
        if red < 100 and green < 100 and blue < 100: red = green = blue = 100  # sorgt dafür, dass es nicht zu dunkel wird
        self.preview_color_scheme = color_scheme.EditableColorScheme((red, green, blue))
        self.color_preview.rectangle.color = self.preview_color_scheme.color
        self.color_preview.borderRectangle.color = self.preview_color_scheme.border
        self.color_preview.label.color = self.preview_color_scheme.text

    def button_active(self, data):
        self.color_picker_red.set_active(True if data == "red" else False)
        self.color_picker_green.set_active(True if data == "green" else False)
        self.color_picker_blue.set_active(True if data == "blue" else False)

    def dispose_subs(self):  # Muss getriggert werden, wenn der Screen gewechselt wird.
        self.disposable.dispose()

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
