from pyglet.graphics import Batch
from reactivex import Observable

import color_scheme
import textprovider.statistical
from controller import Screen
from controller.inputbox import InputBox
from ui_elements_ex import Rect, rx, Style, map_inner_perc, rmap


class SandboxLevel(Screen):

    def __init__(self, events):
        super().__init__()
        pos = events.size.pipe(rmap(lambda size: Rect(0, 0, *size)))
        style = Style(events.color_scheme, "Monocraft", 15)
        self.batch = batch = Batch()

        self.text_provider = textprovider.statistical.StatisticalTextProvider.from_pickle("assets/text_statistics/stats_1.pickle")

        self.generation_args = textprovider.TextProviderArgs(100, 200, textprovider.Charset.ALPHA)
        text = self.text_provider.get_text(self.generation_args)
        self.input_box = InputBox(text, pos.pipe(map_inner_perc(15, 5, 70, 30)), style, events, batch)


    def get_view(self):
        return self.batch