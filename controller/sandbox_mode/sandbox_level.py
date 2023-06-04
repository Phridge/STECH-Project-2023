from pyglet.graphics import Batch, Group
from reactivex import Observable, Observer, combine_latest as combine
from reactivex.operators import combine_latest, filter as rfilter, do_action

import color_scheme
import textprovider.statistical
import ui_elements
from controller import Screen
from controller.inputbox import InputBox
from input_tracker import InputAnalysis
from tools.save_and_open import save_text_tracker
from ui_elements_ex import Rect, rx, Style, map_inner_perc, rmap, BorderedLabel, Button, ToggleButton, Rectangle
from events import Var, Event


class SandboxLevel(Screen):
    """
    Screen-Klasse für ein Sandbox-level.
    """

    def __init__(self, events, save):
        """
        Initiialisiere ein Sandboxlevel.
        :param events: Events-Objekt.
        :param save: Spielstand als int.
        """
        super().__init__()
        pos = events.size.pipe(rmap(lambda size: Rect(0, 0, *size)))
        style = Style(events.color_scheme, "Monocraft", 15)
        self.batch = batch = Batch()
        background = Group(0)
        foreground = Group(1)

        # hintergrund
        self.gif = ui_elements.Gif("assets/images/sandbox_mode_background.gif", 0, 0, 100, 120, 10, True, events,
                                   self.batch, background)
        # um den hintergrund nicht so grell zu machen, ein halbdurchsichtiges rect davor :D
        self.gif = Rectangle(pos, (0, 0, 0, 100), batch, foreground)

        # textgenerator
        self.text_provider = textprovider.statistical.StatisticalTextProvider.from_pickle("assets/text_statistics/stats_1.pickle")

        # hier werden die ausgewählten charsets reingeschickt.
        charsets = Event()
        # aus ausgewählten Charsets werden Textgenerator-Configs berechnet.
        settings = charsets.pipe(
            rmap("".join),
            rmap(lambda s: textprovider.TextProviderArgs(100, 200, s if s else "bro")) # extra case falls nichts ausgewählt wird
        )

        # wird abgefeuert, wenn der angezeigte Text neu generiert werden soll.
        # beispielsweise wenn "neu" oder einer der auswahl-toggles gedrückt wurde.
        regenerate = Var(None)

        def generate_text(data):
            """
            Generiere Text aus configs
            :param data: config
            :return: generierter Text
            """
            return self.text_provider.get_text(data[0])

        # Text observable, berechnet aus s. oben
        text = settings.pipe(
            combine_latest(regenerate),
            rmap(generate_text)
        )

        # eingabebox
        self.input_box = InputBox(text, pos.pipe(map_inner_perc(15, 10, 70, 30)), style, events, batch=batch, group=foreground)
        self._subs.add(
            self.input_box.text_tracker.pipe(
                rfilter(lambda tt: tt.is_finished),
                do_action(lambda tt: save_text_tracker(save, "sandbox", tt)),
            ).subscribe(regenerate)  # neuer text wenn fertig geschrieben.
        )

        # Titel
        self.title = BorderedLabel("Sandbox-Modus", pos.pipe(map_inner_perc(35, 85, 30, 10)), style, batch, foreground)

        # region, in der sich die Optionen-Buttons sich befinden
        button_region = pos.pipe(map_inner_perc(10, 60, 80, 10))

        # Regenerieren Button. Wird dieser geklickt, wird regenerate aktiviert, neuer text erscheint.
        self.new_text_button = Button("Neu", button_region.pipe(map_inner_perc(100*(0/6), 0, 100/6, 100)), style, events, regenerate, False, batch, foreground)

        # die ganzen buttons, alle in der obigen region (in der mitte des Screens.)
        self.lower_case_toggle = ToggleButton("a-z", button_region.pipe(map_inner_perc(100*(1/6), 0, 100/6, 100)), style, events, False, batch, foreground)
        self.upper_case_toggle = ToggleButton("A-Z", button_region.pipe(map_inner_perc(100*(2/6), 0, 100/6, 100)), style, events, False, batch, foreground)
        self.numbers_toggle = ToggleButton("0-9", button_region.pipe(map_inner_perc(100*(3/6), 0, 100/6, 100)), style, events, False, batch, foreground)
        self.easy_punct_toggle = ToggleButton(".,?*", button_region.pipe(map_inner_perc(100*(4/6), 0, 100/6, 100)), style, events, False, batch, foreground)
        self.all_punct_toggle = ToggleButton("[]\\()", button_region.pipe(map_inner_perc(100*(5/6), 0, 100/6, 100)), style, events, False, batch, foreground)

        # lowercase-Buchstaben werden standartmäßig angeschaltet
        self.lower_case_toggle.toggle.on_next(True)


        # Hier werden alle toggle-zustände in ausgewählte Charsets zum generieren verwandelt.
        # jedes mal, wenn ein Toggle gedrückt wird, ändert sich das Charset, entsprechd auch die Configs zum Generieren
        # und somit der Angezeigte text
        # folgender kommentar wichtig
        # noinspection PyArgumentList
        self._subs.add(
            combine(
                self.lower_case_toggle.toggle,
                self.upper_case_toggle.toggle,
                self.numbers_toggle.toggle,
                self.easy_punct_toggle.toggle,
                self.all_punct_toggle.toggle
            ).pipe(
                rmap(lambda toggles: {charset for include, charset in zip(toggles, textprovider.ALL_CHARSETS) if include})
            ).subscribe(charsets)
        )

        from ..settings import SettingsScreen
        from ..home_screen import HomeScreen

        # navigationselemente
        small_style = Style(style.color, style.font, 10)
        self.settings_button = Button(
            "Einstellungen",
            pos.pipe(map_inner_perc(2.5, 85, 12.5, 10)),
            small_style,
            events,
            Observer(lambda _: self.push_screen(SettingsScreen.init_fn(save))),
            False,
            batch=batch,
            group=foreground
        )
        self.leave_button = Button(
            "Verlassen",
            pos.pipe(map_inner_perc(85, 85, 12.5, 10)),
            small_style,
            events,
            Observer(lambda _: self.go_back()),
            False,
            batch=batch,
            group=foreground
        )


    def get_view(self):
        return self.batch