import pyglet
import pygame
from pygame import mixer
import contextlib

import color_scheme
import main_controller
import ui_elements
from reactivex import concat
from reactivex.operators import delay, map as rmap, combine_latest, do_action, starmap, filter as rfilter, share
from reactivex.disposable import CompositeDisposable, Disposable
from controller import Screen
from controller.actors import ThePlayer, combine_offset
from controller.inputbox import InputBox
from . import Machine, animate, Level
from input_tracker import InputAnalysis
from tools.save_and_open import save_run
from ui_elements_ex import Rect, map_inner_perc, Style, Rectangle
from events import Event, Var
from ..level_finished import LevelFinishedScreen

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

Bitte hilf mir meine Freunde, die vom Maschinenkönig in der Dampfstadt gefangen halten werden, zu befreien!

Hoffentlich habe ich genug Ersatz-Teetassen mit. Ohne mein Lebenselixier geht nichts!

*Schlürf* Tee ist einfach das Beste!

Und jetzt los, wir haben viel zu tun!\
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

        # Region, in dem sich der spieler bewegen darf. Die untere kante stellt den laufsteg dar.
        player_area = pos.pipe(
            map_inner_perc(0, 40, 100, 60)
        )

        # Spieler-Objekt.
        player_pos = Event()  # um seine Position zu steuern
        self.p = ThePlayer(
            pos=player_pos.pipe(combine_offset(player_area)),  #position brauch globales offset
            look_dir=Var(1),
            state=Var(ThePlayer.Idle()), # von außen dann über self.p.state steuerbar
            batch=self.batch, group=self.foreground
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
        self.header = ui_elements.BorderedRectangle("Level 1: Der Hafen der Freiheit", 25, 80, 50, 15, self.events.color_scheme, color_scheme.Minecraft, 3.5, self.events, self.batch, self.foreground)

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
            player_anim = animate(-300, 100, 5.0, events.update, lambda v: Rect(v, 0, 150, 150))
            # Das Rechteck für den FAde
            overlay_rect = Rectangle(pos, color, self.batch, self.overlay)

            # den Spieler zum Laufen bringen.
            self.p.state.on_next(ThePlayer.Running(2.0))

            return CompositeDisposable(
                overlay_rect,
                player_anim.subscribe(player_pos.on_next, on_completed=lambda: machine.next()),
                Disposable(lambda: self.p.state.on_next(ThePlayer.Idle())),  # wenn fertig, dann spieler stoppen.
            )

        def player_exit():
            """
            Wie player_entry, nur umgekehrt.
            """
            # save game
            save_run(save, "story_level_1", input_analysis)

            color = concat(
                animate(0, 0, 2.0, events.update, lambda o: (0, 0, 0, int(o))),
                animate(0, 255, 3.0, events.update, lambda o: (0, 0, 0, int(o)))
            )
            pos_anim = animate(100, 2000, 10.0, events.update, lambda v: Rect(v, 0, 150, 150))

            overlay_rect = Rectangle(pos, color, self.batch, self.overlay)

            print(calculate_points(input_analysis))

            self.p.state.on_next(ThePlayer.Running(4.0))
            return CompositeDisposable(
                overlay_rect,
                pos_anim.subscribe(player_pos.on_next),
                color.subscribe(on_completed=lambda: machine.next())
            )

        def show_results():
            print("Level abgeschlossen")
            self.push_screen(LevelFinishedScreen.init_fn(save, "Level2", calculate_points(input_analysis)))


        from main_controller import PushScreen
        def goto(screen_init):
            return lambda _: self.game_command.on_next(PushScreen(screen_init))


        # Erstellung der State Machine aus allen nötigen Zuständen:
        # Spieler entry
        # dann die ganzen texte
        # dann Spieler exit
        machine = Machine(
            [player_entry]
            + [display_text(text) for text in self.TEXTS[:1]]
            + [player_exit]
            + [show_results]
        )


        def calculate_points(input_analysis: InputAnalysis):
            return int((input_analysis.correct_char_count / input_analysis.time) ** 2 * 100)

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch

    def play_music(self, nextmusic):
        with contextlib.suppress(pygame.error):
            mixer.init()
            mixer.music.load(nextmusic)
            mixer.music.play()
            mixer.music.play(-1)