from pyglet.graphics import Batch
from reactivex import Observable, Observer, combine_latest as combine
from reactivex.operators import combine_latest

import color_scheme
import textprovider.statistical
from controller import Screen
from controller.inputbox import InputBox
from ui_elements_ex import Rect, rx, Style, map_inner_perc, rmap, BorderedLabel, Button, ToggleButton
from events import Var, Event


class SandboxLevel(Screen):

    def __init__(self, events):
        super().__init__()
        pos = events.size.pipe(rmap(lambda size: Rect(0, 0, *size)))
        style = Style(events.color_scheme, "Monocraft", 15)
        self.batch = batch = Batch()

        self.text_provider = textprovider.statistical.StatisticalTextProvider.from_pickle("assets/text_statistics/stats_1.pickle")

        charsets = Event()
        settings = charsets.pipe(
            rmap("".join),
            rmap(lambda s: textprovider.TextProviderArgs(100, 200, s if s else "bro")) # extra case falls nichts ausgewählt wird
        )
        regenerate = Var(None)

        def generate_text(data):
            return self.text_provider.get_text(data[0])

        text = settings.pipe(
            combine_latest(regenerate),
            rmap(generate_text)
        )

        self.input_box = InputBox(text, pos.pipe(map_inner_perc(15, 10, 70, 30)), style, events, batch)
        self.title = BorderedLabel("Sandbox-Modus", pos.pipe(map_inner_perc(35, 85, 30, 10)), style, batch)

        button_region = pos.pipe(map_inner_perc(10, 60, 80, 10))

        self.new_text_button = Button("Neu", button_region.pipe(map_inner_perc(100*(0/6), 0, 100/6, 100)), style, events, Observer(regenerate.on_next), batch)

        self.lower_case_toggle = ToggleButton("a-z", button_region.pipe(map_inner_perc(100*(1/6), 0, 100/6, 100)), style, events, batch)
        self.upper_case_toggle = ToggleButton("A-Z", button_region.pipe(map_inner_perc(100*(2/6), 0, 100/6, 100)), style, events, batch)
        self.numbers_toggle = ToggleButton("0-9", button_region.pipe(map_inner_perc(100*(3/6), 0, 100/6, 100)), style, events, batch)
        self.easy_punct_toggle = ToggleButton(".,?*", button_region.pipe(map_inner_perc(100*(4/6), 0, 100/6, 100)), style, events, batch)
        self.all_punct_toggle = ToggleButton("[]\\()", button_region.pipe(map_inner_perc(100*(5/6), 0, 100/6, 100)), style, events, batch)

        self.lower_case_toggle.toggle.on_next(True)

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


    def get_view(self):
        return self.batch