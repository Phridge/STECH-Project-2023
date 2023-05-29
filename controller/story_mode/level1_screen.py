import pyglet
import pygame
from pygame import mixer
import contextlib

import color_scheme
import ui_elements
from reactivex.operators import delay, map as rmap, combine_latest, do_action, starmap, filter as rfilter
from reactivex.disposable import CompositeDisposable, Disposable
from controller import Screen
from controller.actors import ThePlayer
from controller.inputbox import InputBox
from . import Machine, animate, Level
from input_tracker import InputAnalysis
from tools.save_and_open import save_run
from ui_elements_ex import Rect, map_inner_perc, Style, Rectangle
from events import Event

"""
Eine Vorlage für einen Screen. ab Zeile 22 können Elemente eingefügt werde. Ein paar der ui-Elements sind als Beispiel gezeigt.
In dieser Datei sind nur die absoluten Essentials drin. Hinzufügen ist kein Problem, löschen schon.
Lasst euch dieses Template anzeigen, indem ihr es im main_controller als initialen Controller setzt :D
"""


class Level1(Level):

    TEXTS = """\
Hallo! Ich bin Maxwell.

Schön, dass du dich entschieden hast, das 10-Finger-Schreiben zu lernen.

Je schneller du schreibst, desto mehr Punkte warten am Ende jeden Levels auf dich.

Doch zunächst muss ich erstmal meine Freunde, die vom Maschinenkönig in der Dampfstadt gefangen halten werden, befreien!

Die Reise wird lang und herausfordernd, hoffentlich habe ich genug Ersatz-Teetassen mit. Ohne mein Lebenselixier geht nichts!

*SSSSSSSsssssssssssssssssip*

...genug Tee, nun gehts los!\
""".split("\n\n")

    def __init__(self, events, save):
        super().__init__()
        self.events = events
        pos = events.size.pipe(
            rmap(lambda s: Rect(0, 0, *s))
        )
        style = Style(events.color_scheme, "Monocraft", 15)

        # hintergrund
        self.gif = ui_elements.Gif("assets/images/port.gif", 0, 0, 100, 100, 30, True, self.events, self.batch, self.background)

        # Player-Objekt
        # player = Player(self.events, self.batch, 20, 40, 20, 30)


        # Spieler-Objekt. Bis is eine Position erhält, ist es nicht sichtbar.
        self.p = ThePlayer(batch=self.batch, group=self.foreground)
        # Region, in dem sich der spieler bewegen darf. Die untere kante stellt den laufsteg dar.
        player_area = pos.pipe(
            map_inner_perc(0, 40, 100, 60)
        )

        # event, welches von der Machine s. unten den anzuzeigenden Text erhält-
        text = Event()

        # um die Spielereingaben Textübergreifend zu sammeln und in die Datenbank zu speicher.
        input_analysis = InputAnalysis()
        self.input_box = InputBox(text, pos.pipe(map_inner_perc(10, 5, 80, 20)), style, events, input_analysis, batch=self.batch, group=self.foreground)
        # ist ein Text fertig geschrieben, wird die Machine um einen Schritt vorangebracht.
        self._subs.add(
            self.input_box.text_tracker.pipe(
                rfilter(lambda tt: tt.is_finished)
            ).subscribe(lambda _: machine.next())
        )

        # Überschrift.
        self.header = ui_elements.BorderedRectangle("Level 1: Der Hafen der Freiheit", 20, 80, 60, 20, self.events.color_scheme, color_scheme.Minecraft, 2, self.events, self.batch, self.foreground)

        def display_text(display_text):
            """
            Factory-Funktion, um einfach den nächsten Text in der Input-Box anzuzeigen.
            :param display_text: Zu schreibender Text.
            :return: eine Funktion, die von der Machine ausgeführt werden kann.
            """
            return lambda: text.on_next(display_text)

        def player_entry():
            """
            Eröffnung des Levels.

            Der Bildschirm faded von Schwarz zu durchsichtig, und der Spieler läuft von der Linken seite ein.
            :return: Nachher zu löschenden Ressourcen.
            """
            # farbanimation
            color = animate(255, 0, 3.0, events.update, lambda o: (0, 0, 0, int(o)))
            # spielerpositionsanimation.
            # Sieht kompliziert aus, da noch die Position des Laufstegs mit berücksichtigt werden muss.
            player_pos = animate(-300, 100, 5.0, events.update).pipe(
                do_action(on_completed=lambda: machine.next()),  # wenn die animation durch ist, nächster Zustand
                combine_latest(player_area),
                starmap(lambda xoff, area: Rect(xoff, 0, 150, 150).offset(area)),
            )
            # Das Rechteck für den FAde
            overlay_rect = Rectangle(pos, color, self.batch, self.overlay)

            # den Spieler zum Laufen bringen.
            self.p.running_speed.on_next(2.0)
            return CompositeDisposable(
                overlay_rect,
                player_pos.subscribe(self.p.pos),
                Disposable(lambda: self.p.running_speed.on_next(0.0))  # wenn fertig, dann spieler stoppen.
            )

        def player_exit():
            """
            Wie player_entry, nur umgekehrt.
            """
            # save game
            save_run(save, "story_level_1", input_analysis)

            color = animate(0, 255, 3.0, events.update, lambda o: (0, 0, 0, int(o))).pipe(delay(3.0))
            player_pos = animate(100, 2000, 10.0, events.update).pipe(
                do_action(on_completed=lambda: machine.next()),
                combine_latest(player_area),
                starmap(lambda xoff, area: Rect(xoff, 0, 150, 150).offset(area)),
            )

            overlay_rect = Rectangle(pos, color, self.batch, self.overlay)

            print(calculate_points(input_analysis))

            self.p.running_speed.on_next(4.0)
            return CompositeDisposable(
                overlay_rect,
                player_pos.subscribe(self.p.pos),
            )

        # Erstellung der State Machine aus allen nötigen Zuständen:
        # Spieler entry
        # dann die ganzen texte
        # dann Spieler exit
        machine = Machine(
            [player_entry]
            + [display_text(text) for text in self.TEXTS]
            + [player_exit]
        )

        def calculate_points(input_analysis: InputAnalysis):
            return int((input_analysis.correct_char_count / input_analysis.time) * 100)


    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch

    def play_music(self, nextmusic):
        with contextlib.suppress(pygame.error):
            mixer.init()
            mixer.music.load(nextmusic)
            mixer.music.play()
            mixer.music.play(-1)