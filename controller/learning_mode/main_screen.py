import pyglet
import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable

from controller import Controller, Screen
from controller.learning_mode.learning_level import LearningLevel
from controller.settings import SettingsScreen
from controller.statistics import StatisticsScreen


from ui_elements_ex import Rect, rx, Style, map_inner_perc, rmap, BorderedLabel, Button, ToggleButton
from events import Var, Event
from reactivex import concat, just, Observer
from reactivex.operators import repeat, combine_latest, sample, scan
from operator import itemgetter


def make_levels(focus_chars):
    levels = []
    all_chars = ""
    for focus in focus_chars:
        all_chars += focus
        levels.append((focus, all_chars))
    return levels



LEVELS = make_levels([
    "dfjk",
    "ru",
    "ei",
    "vm",
    "bn",
    "tz",
    "ei",
    "sl",
    "aö",
    "wo",
    "qp",
    "xy",
    "üä",
    "1234567890",
    ",.-!?",
])

class MainLearningScreen(Screen):
    def __init__(self, events, save):
        super().__init__()
        self.batch = batch = pyglet.graphics.Batch()

        pos = events.size.pipe(rmap(lambda size: Rect(0, 0, *size)))
        style = Style(events.color_scheme, "Monocraft", 15)

        # Layout für den Startbildschirm des Lern-Modus
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, self.batch)
        self.header = ui_elements.BorderedRectangle("Lernen", 20, 75, 60, 20, events.color_scheme, color_scheme.Minecraft, 4, events, self.batch)

        self.back = ui_elements.InputButton("Zurück", 40, 10, 20, 10, events.color_scheme, color_scheme.Minecraft, 10, events, self.batch)
        self.settings = ui_elements.InputButton("Einstellungen", 2.5, 85, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 8, events, self.batch)
        self.statistics = ui_elements.InputButton("Statistiken", 85, 85, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 8.4, events, self.batch)

        # level anzeigen
        change_level_index = Var(0)
        level_selection = change_level_index.pipe(
            scan(lambda curr, chng: (curr + chng + len(LEVELS)) % len(LEVELS), 0),
            rmap(LEVELS.__getitem__),
        )
        select_level_event = Event()
        self.level_selector = Button(
            level_selection.pipe(rmap(itemgetter(0))),
            pos.pipe(map_inner_perc(30, 30, 40, 40)),
            style,
            events,
            select_level_event,
            batch)
        self.prev_level = Button(
            "<",
            pos.pipe(map_inner_perc(15, 30, 10, 40)),
            style,
            events,
            Observer(lambda _: change_level_index.on_next(-1)),
            batch
        )
        self.next_level = Button(
            ">",
            pos.pipe(map_inner_perc(75, 30, 10, 40)),
            style,
            events,
            Observer(lambda _: change_level_index.on_next(+1)),
            batch
        )


        # wenn ein level ausgewählt wird, wird zum entsprechenden Level gewechselt
        self._subs.add(select_level_event.pipe(
            combine_latest(level_selection),
        ).subscribe(lambda data: self.go_to(LearningLevel.init_fn(*data[1], save))))

        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        self._subs.add(self.back.clicked.subscribe(lambda _: self.go_back()))
        self._subs.add(self.settings.clicked.subscribe(lambda _: self.push_screen(SettingsScreen.init_fn(save))))
        self._subs.add(self.statistics.clicked.subscribe(lambda _: self.push_screen(StatisticsScreen.init_fn(save))))

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
