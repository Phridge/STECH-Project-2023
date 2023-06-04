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
    """
    Erstellt die Leveldaten für die verschiedenen Buchstabengruppen

    :param focus_chars: Chars, für die das Level erstellt wird
    """
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
    """
    Übersichts-Screen zum auswählen vom Lern-Level.
    """
    def __init__(self, events, save):
        """
        Erstelle den den Übersichts-Screen.
        :param events: Events-objekt
        :param save: spielstandsnummer
        """
        super().__init__()
        self.batch = batch = pyglet.graphics.Batch()

        pos = events.size.pipe(rmap(lambda size: Rect(0, 0, *size)))
        style = Style(events.color_scheme, "Monocraft", 15)

        # Layout für den Startbildschirm des Lern-Modus
        self.background = ui_elements.Sprite("assets/images/StartScreenBackground.png", 0, 0, 100, 100, events, self.batch)
        self.header = ui_elements.BorderedRectangle("Lernen", 20, 75, 60, 20, events.color_scheme, color_scheme.Minecraft, 4, events, self.batch)

        # navigationselemente
        self.back = ui_elements.InputButton("Zurück", 40, 5, 20, 10, events.color_scheme, color_scheme.Minecraft, 10, events, self.batch)
        self.settings = ui_elements.InputButton("Einstellungen", 2.5, 85, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 8, events, self.batch)
        self.statistics = ui_elements.InputButton("Statistiken", 85, 85, 12.5, 10, events.color_scheme, color_scheme.Minecraft, 8.4, events, self.batch)

        # level anzeigen
        change_level_index = Var(0)  # änderungs-events für den level-index. hier -1 oder +1 reinsenden um level index zu ändern
        level_index = change_level_index.pipe(  # rotiert den levelindex, je nach dem was bei change_level_index reinkommt
            scan(lambda curr, chng: (curr + chng + len(LEVELS)) % len(LEVELS), 0),
        )
        level_selection = level_index.pipe(  # index zu leveldaten.
            rmap(LEVELS.__getitem__),
        )

        # in dieses event wird ein None reingeschickt, wenn der Button geklickt wurde. Darauf wird weiter unten drauf reagiert und
        # zum entsprechenden screen gewechselt
        select_level_event = Event()

        # Button, bei dem angezeigt wird, welches level gestartet wird bei press. dafür werden die aktuellen Leveldaten[0] genommen
        self.level_selector = Button(
            level_selection.pipe(rmap(itemgetter(0))),
            pos.pipe(map_inner_perc(30, 20, 40, 40)),
            style,
            events,
            select_level_event,
            batch=batch
        )

        # vorheriges-level button
        self.prev_level = Button(
            "<",
            pos.pipe(map_inner_perc(15, 20, 10, 40)),
            style,
            events,
            Observer(lambda _: change_level_index.on_next(-1)),
            batch=batch
        )

        # nächstes level button
        self.next_level = Button(
            ">",
            pos.pipe(map_inner_perc(75, 20, 10, 40)),
            style,
            events,
            Observer(lambda _: change_level_index.on_next(+1)),
            batch=batch
        )

        # anzeige, das wievielste level aktuell ausgewählt ist.
        self.level_index_label = BorderedLabel(
            level_index.pipe(
                rmap(lambda i: f"{i+1}/{len(LEVELS)}")
            ),
            pos.pipe(map_inner_perc(40, 62, 20, 7)),
            style,
            batch=batch
        )


        # wenn ein level ausgewählt wird, wird zum entsprechenden Level gewechselt
        self._subs.add(select_level_event.pipe(
            combine_latest(level_selection),
        ).subscribe(lambda data: self.push_screen(LearningLevel.init_fn(*data[1], save))))

        # Fängt ab, wenn Buttons gedrückt werden und erzeugt Subscriptions
        self._subs.add(self.back.clicked.subscribe(lambda _: self.go_back()))
        self._subs.add(self.settings.clicked.subscribe(lambda _: self.push_screen(SettingsScreen.init_fn(save))))
        self._subs.add(self.statistics.clicked.subscribe(lambda _: self.push_screen(StatisticsScreen.init_fn(save))))

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch
