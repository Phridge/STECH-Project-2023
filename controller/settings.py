import pyglet

import color_scheme
import ui_elements
from controller import Screen


class SettingsScreen(Screen):
    def __init__(self, events, save):
        super().__init__()
        self.batch = pyglet.graphics.Batch()
        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        background = pyglet.graphics.Group(order=-1)
        foreground = pyglet.graphics.Group(order=1)

        self.preview_color_scheme = events.color_scheme  # aktuelles Color_scheme
        self.volume_value = events.volume.value
        self.fullscreen = events.fullscreen
        self.new_screen_size = None

        # Layout für den Einstellungs-Bildschirm
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, self.batch)
        self.header = ui_elements.BorderedRectangle("Einstellungen", 20, 75, 60, 20, events.color_scheme, color_scheme.Minecraft, 4, events, self.batch)

        # Color-Picker
        self.color = ui_elements.BorderedRectangle("Farbe:", 2.5, 55, 15, 10, events.color_scheme, color_scheme.Minecraft, 10, events, self.batch)
        self.color_picker_red = ui_elements.SettingTextField(str(self.preview_color_scheme.border[0]), 3, 255, 20, 55, 18.3333, 10, color_scheme.EditableColorScheme((255, 0, 0)), color_scheme.Minecraft, 15, events, "red", self.batch)
        self.color_picker_green = ui_elements.SettingTextField(str(self.preview_color_scheme.border[1]), 3, 255, 40.8333, 55, 18.3333, 10, color_scheme.EditableColorScheme((0, 255, 0)), color_scheme.Minecraft, 15, events, "green", self.batch)
        self.color_picker_blue = ui_elements.SettingTextField(str(self.preview_color_scheme.border[2]), 3, 255, 61.6666, 55, 18.3333, 10, color_scheme.EditableColorScheme((0, 0, 255)), color_scheme.Minecraft, 15, events, "blue", self.batch)
        self.color_preview = ui_elements.BorderedRectangle("Beispiel", 82.5, 55, 15, 10, self.preview_color_scheme, color_scheme.Minecraft, 11, events, self.batch)

        # Volume-Picker
        self.volume = ui_elements.BorderedRectangle("Lautstärke:", 2.5, 42.5, 15, 10, events.color_scheme, color_scheme.Minecraft, 8.5, events, self.batch)
        self.volume_picker = ui_elements.SettingTextField(str(int(events.volume.value * 100)), 3, 100, 40.8333, 42.5, 18.3333, 10, events.color_scheme, color_scheme.Minecraft, 15, events, "volume", self.batch)

        # Fenster-Einstellungen
        self.window = ui_elements.BorderedRectangle("Fenster:", 2.5, 30, 15, 10, events.color_scheme, color_scheme.Minecraft, 10, events, self.batch)
        self.fullscreen_toggle_button = ui_elements.InputButton("", 20, 30, 18.3333, 10, events.color_scheme, color_scheme.Minecraft, 8, events, self.batch)
        if self.fullscreen is False:
            self.fullscreen_toggle_button.label.text = "Vollbild an"
        else:
            self.fullscreen_toggle_button.label.text = "Vollbild aus"
        self.window_x = ui_elements.SettingTextField("Breite", 4, 9999, 40.8333, 30, 18.3333, 10, events.color_scheme, color_scheme.Minecraft, 10, events, "x", self.batch)
        self.window_y = ui_elements.SettingTextField("Höhe", 4, 9999, 61.6666, 30, 18.3333, 10, events.color_scheme, color_scheme.Minecraft, 10, events, "y", self.batch)

        # Menü-Buttons
        self.back = ui_elements.InputButton("Zurück", 20, 10, 20, 10, events.color_scheme, color_scheme.Minecraft, 8, events, self.batch)
        self.apply_button = ui_elements.InputButton("Anwenden", 60, 10, 20, 10, events.color_scheme, color_scheme.Minecraft, 8, events, self.batch)

        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        from main_controller import PopScreen

        self._subs.add(self.back.clicked.subscribe(lambda _: self.game_command.on_next(PopScreen())))
        self._subs.add(self.fullscreen_toggle_button.clicked.subscribe(lambda _: self.set_fullscreen(not self.fullscreen)))
        self._subs.add(self.window_x.clicked.subscribe(lambda _: self.set_button_active("x")))
        self._subs.add(self.window_x.changed.subscribe(self.change_size))
        self._subs.add(self.window_y.clicked.subscribe(lambda _: self.set_button_active("y")))
        self._subs.add(self.window_y.changed.subscribe(self.change_size))
        self._subs.add(self.apply_button.clicked.subscribe(lambda _: self.apply_changes(save)))
        self._subs.add(self.color_picker_red.changed.subscribe(self.change_color))
        self._subs.add(self.color_picker_red.clicked.subscribe(lambda _: self.set_button_active("red")))
        self._subs.add(self.color_picker_green.changed.subscribe(self.change_color))
        self._subs.add(self.color_picker_green.clicked.subscribe(lambda _: self.set_button_active("green")))
        self._subs.add(self.color_picker_blue.changed.subscribe(self.change_color))
        self._subs.add(self.color_picker_blue.clicked.subscribe(lambda _: self.set_button_active("blue")))
        self._subs.add(self.volume_picker.changed.subscribe(self.change_volume))
        self._subs.add(self.volume_picker.clicked.subscribe(lambda _: self.set_button_active("volume")))
        self._subs.add(events.key.subscribe(self.set_button_active))


    def apply_changes(self, save):
        """
        Lädt den SettingsScreen neu, nachdem die Einstellungen angewandt wurden
        """
        from main_controller import ChangeSetting, SwitchScreen, SetFullscreen, ReloadScreen

        # self.event.on_next(("ChangeColorScheme", self.preview_color_scheme))
        self.game_command.on_next(ChangeSetting("color_scheme", self.preview_color_scheme))

        # self.event.on_next(("ChangeVolume", self.volume_value))
        self.game_command.on_next(ChangeSetting("volume", self.volume_value))

        if not self.fullscreen and self.new_screen_size:
            # self.event.on_next(("ChangeScreenSize", self.new_screen_size[0], self.new_screen_size[1]))
            self.game_command.on_next(ChangeSetting("size", self.new_screen_size))

        # self.change_controller.on_next(("ReloadSettings", previous_controller, data))
        self.game_command.on_next(ReloadScreen())

    def change_color(self, _):
        """
        Ändert das Farbschema des gesamten Spiels und aktualisiert die Preview-Box
        """
        if self.color_picker_red.text.isnumeric():
            red = int(self.color_picker_red.text)
        else:
            red = 0
        if self.color_picker_green.text.isnumeric():
            green = int(self.color_picker_green.text)
        else:
            green = 0
        if self.color_picker_blue.text.isnumeric():
            blue = int(self.color_picker_blue.text)
        else:
            blue = 0
        if red < 100 and green < 100 and blue < 100: red = green = blue = 100  # sorgt dafür, dass es nicht zu dunkel wird
        print(red, green, blue)
        self.preview_color_scheme = color_scheme.EditableColorScheme((red, green, blue))
        self.color_preview.rectangle.color = self.preview_color_scheme.color
        self.color_preview.borderRectangle.color = self.preview_color_scheme.border
        self.color_preview.label.color = self.preview_color_scheme.text

    def set_button_active(self, data):
        """
        Sorgt dafür, dass in den Einstellungen immer nur ein Button gleichzeitig Inputs annehmen kann

        :param data: String mit Button, der Aktiv gesetzt werden soll
        """
        if data[0] == 65289 and data[1] == 16:  # falls tab gedrückt wird
            if self.color_picker_red.active: data = "green"
            elif self.color_picker_green.active: data = "blue"
            elif self.color_picker_blue.active: data = "volume"
            elif self.volume_picker.active: data = "x"
            elif self.window_x.active: data = "y"
            else: data = "red"

        if data[0] == 65289 and data[1] == 17:  # falls shift + tab gedrückt wird
            if self.color_picker_red.active: data = "y"
            elif self.color_picker_green.active: data = "red"
            elif self.color_picker_blue.active: data = "green"
            elif self.volume_picker.active: data = "blue"
            elif self.window_x.active: data = "volume"
            else: data = "x"

        if type(data) != tuple:
            self.color_picker_red.set_active(True if data == "red" else False)
            self.color_picker_green.set_active(True if data == "green" else False)
            self.color_picker_blue.set_active(True if data == "blue" else False)
            self.volume_picker.set_active(True if data == "volume" else False)
            self.window_x.set_active(True if data == "x" else False)
            self.window_y.set_active(True if data == "y" else False)

    def change_volume(self, data):
        """
        Korrigiert den Input von 0-100 auf 0-1, damit das Pyglet den Wert verwenden kann
        """
        if self.volume_picker.text.isnumeric():
            self.volume_value = int(self.volume_picker.text) / 100
        else:
            self.volume_value = 0
        from main_controller import ChangeSetting
        self.game_command.on_next(ChangeSetting("volume", self.volume_value))

    def set_fullscreen(self, state):
        """
        Ändert zu Fullscreen bzw zu Fenstermodus

        :param fullscreen_state: Bool, ob das Fenster momentan im Fullscreen-Modus ist
        """
        self.fullscreen = state
        self.fullscreen_toggle_button.label.text = "Vollbild an" if not state else "Vollbild aus"

        from main_controller import SetFullscreen
        self.game_command.on_next(SetFullscreen(state))

    def change_size(self, data):
        x = y = None
        if self.window_x.label.text.isnumeric():
            x = int(self.window_x.label.text)
        elif self.window_x.label.text != "Höhe" and self.window_x.label.text != "":
            x = 300
        if self.window_y.label.text.isnumeric():
            y = int(self.window_y.label.text)
        elif self.window_y.label.text != "Höhe" and self.window_y.label.text != "":
            y = 300
        if x and x < 300: x = 300
        if y and y < 300: y = 300  # sorgt dafür, dass es nicht zu dunkel wird
        if str(x).isnumeric() and str(y).isnumeric():
            self.new_screen_size = (int(x), int(y))

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
