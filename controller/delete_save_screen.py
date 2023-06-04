import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable

from controller import Screen
from tools import save_and_open


class DeleteSaveScreen(Screen):
    def __init__(self, events, save):
        super().__init__()
        self.batch = pyglet.graphics.Batch()
        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        background = pyglet.graphics.Group(order=-1)
        foreground = pyglet.graphics.Group(order=1)

        # Design
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, self.batch)
        self.header = ui_elements.BorderedRectangle("Spielstand " + str(save) + " wirklich löschen?", 20, 75, 60, 20, events.color_scheme, color_scheme.Minecraft, 3.4, events, self.batch)
        self.button1 = ui_elements.InputButton("Ja", 30, 55, 17.5, 10, events.color_scheme, color_scheme.Minecraft, 16, events, self.batch)
        self.button2 = ui_elements.InputButton("Nein", 52.5, 55, 17.5, 10, events.color_scheme, color_scheme.Minecraft, 16, events, self.batch)

        # erstellt Sublist, damit der Screen vollständig verworfen wird
        self._subs.add(self.button1.clicked.subscribe(lambda _: self.delete_save(save)))
        self._subs.add(self.button2.clicked.subscribe(lambda _: self.back_to_menu()))

    def delete_save(self, save):
        """
        Löscht den angegeben save aus der Datenbank und wechselt den Screen
        :param save: zu löschender Save
        """
        save_and_open.delete_save(save)
        self.back_to_menu()

    def back_to_menu(self):  # Wird getriggert, wenn ein Spielstand ausgewählt wird
        from main_controller import PopScreen
        self.game_command.on_next(PopScreen())

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
