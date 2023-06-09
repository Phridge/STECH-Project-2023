from pyglet.graphics import Batch, Group

import color_scheme
import textprovider
import ui_elements
import ui_elements_ex
from textprovider import TextProviderArgs
from textprovider.statistical import StatisticalTextProvider
from textprovider.randomized import RandomTextProvider
from controller import Screen
from tools.save_and_open import save_text_tracker
from ..inputbox import InputBox
from ui_elements_ex import Rect, rx, Style, map_inner_perc, rmap, BorderedLabel, Button, ToggleButton
from events import Var, Event
from reactivex import concat, just, repeat_value, Observer
from reactivex.operators import combine_latest, sample, do_action, zip as rzip, filter as rfilter


class LearningLevel(Screen):
    """
    Screen-Klasse für den Übungsmodus.
    """
    def __init__(self, events, focus_chars, all_chars, save):
        """
        Erstelle ein Learning-Level.

        :param events: Events-Objekt.
        :param focus_chars: Buchstaben, auf die sich in diesem Level sich fokussiert wird.
        :param all_chars: Alle buchstaben, die nach den Fokus-Buchstaben trainiert werden (alle vorherigen buchstaben idr.)
        :param save: spielstand, in den gespeichert wird.
        """
        super().__init__()
        self.level_name = f"learning_{focus_chars}"
        pos = events.size.pipe(rmap(lambda size: Rect(0, 0, *size)))
        style = Style(events.color_scheme, "Monocraft", 15)
        self.batch = batch = Batch()
        background = Group(0)
        foreground = Group(1)

        # hintergrund
        self.gif = ui_elements.Gif("assets/images/learning_mode_background.gif", 0, 0, 100, 120, 2, True, events, self.batch, background)
        self.gif = ui_elements_ex.Rectangle(pos, (0, 0, 0, 100), batch, foreground)

        # textgeneratoren initialisieren
        self.focus_text_provider = RandomTextProvider(5)
        self.text_provider = StatisticalTextProvider.from_pickle("assets/text_statistics/stats_1.pickle") if len(all_chars) > 12 else self.focus_text_provider


        def text_for_round(round):
            """
            Abhängig von der aktuellen Runde wird mit dieser Funktion ein Text generiert.

            :param round: Aktuelle Runde
            """
            provider = self.focus_text_provider if round == 0 else self.text_provider
            args = TextProviderArgs(100, 150, focus_chars) if round == 0 else TextProviderArgs(100, 150, all_chars)
            return provider.get_text(args)


        # titel
        self.title = BorderedLabel(f"Buchstaben {', '.join(focus_chars)}", pos.pipe(map_inner_perc(25, 80, 50, 15)), style, batch, foreground)

        # wieviele runden (nur vorgabe, keine pfilciht) geübt werden sollen
        max_rounds = 5
        # aktuelle runde
        round = Var(0)

        # label zuma nzeigen der Runde
        self.round_label = BorderedLabel(
            round.pipe(
                rmap(lambda p: f"Runde {p}/{max_rounds}"),
            ),
            pos.pipe(map_inner_perc(5, 65, 20, 7)),
            style,
            batch,
            foreground
        )

        # runde zu text
        text = round.pipe(rmap(text_for_round))

        # die eingabebox.
        self.input_box = InputBox(text, pos.pipe(map_inner_perc(15, 10, 70, 30)), style, events, batch=batch, group=foreground)
        self._subs.add(
            self.input_box.text_tracker.pipe(
                rfilter(lambda tt: tt.is_finished),
                do_action(lambda tt: save_text_tracker(save, self.level_name, tt))
            ).subscribe(lambda _: round.on_next(round.value + 1))  # ist ein text fertig geschrieben, wird der nächste Text geladen.
        )

        from ..settings import SettingsScreen
        from ..home_screen import HomeScreen

        self.settings_button = ui_elements.BorderedRectangleButton("Einstellungen", 2.5, 85, 12.5, 10,
                                                                   events.color_scheme, color_scheme.Minecraft, 7,
                                                                   events, batch, foreground)
        self.leave_button = ui_elements.BorderedRectangleButton("Verlassen", 85, 85, 12.5, 10, events.color_scheme,
                                                                color_scheme.Minecraft, 8, events, batch, foreground)
        self._subs.add(self.settings_button.clicked.subscribe(lambda _: self.push_screen(SettingsScreen.init_fn(save))))
        self._subs.add(self.leave_button.clicked.subscribe(lambda _: self.go_back()))

    def get_view(self):
        return self.batch
