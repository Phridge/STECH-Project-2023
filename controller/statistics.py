import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable
import statistic_lib.statistic_view as sv
import statistic_lib.statistics_controller as sc
from controller import Screen


class StatisticsScreen(Screen):
    def __init__(self, events, save):
        super().__init__()
        if save == 0:
            save_text = "Alle Spielstände"
        else:
            save_text = "Spielstand " + str(save)
        self.game_save = save
        width, height = events.size.value
        dpi_res = min(width, height) / 10
        self.fig = sv.Figure((width / dpi_res, height / dpi_res), dpi=dpi_res)
        self.image = pyglet.image.create(width, height).get_texture()
        self.batch = pyglet.graphics.Batch()

        # Instanziiert klassen
        self.current_char = sv.CharView()

        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        background = pyglet.graphics.Group(order=-1)
        foreground = pyglet.graphics.Group(order=1)

        # Layout für den Statistik-Bildschirm
        sv.draw_accuracy_chart(self.fig, 98.6, 37.5, self.current_char.get_char())
        sv.draw_char_pressed_chart(self.fig, 378, 820, self.current_char.get_char())
        sv.draw_time_per_char_chart(self.fig, 997, 222, self.current_char.get_char())
        sv.bigu_graphu(self.fig, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], [1, 7.5, 3, 7, 5, 4, 7, 9, 8, 4, 1],
                       [5, 1, 2, 3, 6.5, 2, 1, 5, 6, 2, 7], self.current_char.get_char())

        sv.update_image(self.fig, self.image)
        self.background = ui_elements.Sprite(self.image, 0, 0, 100, 100, events, self.batch)
        self.header = sv.draw_head_box('Sample', events, self.batch)
        self.button_back = ui_elements.InputButton("Zurück", 1, 93, 20, 7, events.color_scheme,
                                                   color_scheme.Minecraft, 7, events, self.batch)
        self.info_box = ui_elements.BorderedRectangle(save_text, 79, 93, 20, 7,
                                                      color_scheme.BlackWhite,
                                                      color_scheme.Minecraft, 7, events, batch=self.batch)
        self.batch.draw()

        from main_controller import PopScreen
        self._subs.add(events.text.subscribe(self.update_view_on_char_input))
        self._subs.add(self.button_back.clicked.subscribe(lambda _: self.game_command.on_next(PopScreen())))
        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        # from main_controller import PopScreen
        # self._subs.add(self.back.clicked.subscribe(lambda _: self.game_command.on_next(PopScreen())))

    def update_view_on_char_input(self, char):
        """
        Aktualisiert die Anzeige je nach getätigtem Tastendruck
        :param char: Zeichen, das durch Tastendruck getippt wurde
        :return:
        """
        self.current_char.change_char(char)
        print(self.current_char.get_char())
        self.header.label.text = 'Statistics for the char: ' + self.current_char.get_char()
        self.fig.clf()
        last_char_data = sc.get_last_results_of_char(self.game_save, self.current_char.get_char())
        # graphen zeichnen
        sv.draw_accuracy_chart(self.fig, round(sc.get_avg_accuracy_for_char(self.game_save, self.current_char.get_char()), 2),
                               round(last_char_data[4]*100, 2), self.current_char.get_char())
        sv.draw_char_pressed_chart(self.fig, last_char_data[1], last_char_data[2], self.current_char.get_char())
        sv.draw_time_per_char_chart(self.fig, round(sc.get_avg_time_for_char(self.game_save, self.current_char.get_char())*1000),
                                    round(last_char_data[3]*1000), self.current_char.get_char())
        sv.bigu_graphu(self.fig,
                       sc.get_count_with_char(self.game_save, self.current_char.get_char()),
                       sc.get_avg_time_per_char_array(self.game_save, self.current_char.get_char()),
                       sc.get_time_progression(self.game_save, self.current_char.get_char()),
                       self.current_char.get_char())
        sv.update_image(self.fig, self.image)
        self.batch.draw()

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch

    def get_game_save(self):
        return self.game_save
