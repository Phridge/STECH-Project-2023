import contextlib
import itertools

import pygame
import pyglet
from pygame import mixer
from pyglet.graphics import Group
from reactivex import Observable, just, concat
from reactivex.disposable import CompositeDisposable, SerialDisposable, Disposable
from reactivex.operators import combine_latest, map as rmap, share, starmap, scan

import color_scheme
import textprovider.statistical
import ui_elements
from controller.actors import ThePlayer, combine_offset, StaticActor
from events import Var
from input_tracker import InputAnalysis, TextTracker
from tools.save_and_open import save_run
from ui_elements_ex import rx, Rect, Style, map_inner_perc, BorderedLabel, Rectangle
from . import Level, animate, LevelMachine, load_enemy_idle, load_bush, load_enemy_run
from ..inputbox import InputBox
from ..level_finished import LevelFinishedScreen

"""
Eine Vorlage für einen Screen. ab Zeile 22 können Elemente eingefügt werde. Ein paar der ui-Elements sind als Beispiel gezeigt.
In dieser Datei sind nur die absoluten Essentials drin. Hinzufügen ist kein Problem, löschen schon.
Lasst euch dieses Template anzeigen, indem ihr es im main_controller als initialen Controller setzt :D
"""


class Level2Screen(Level):
    def __init__(self, events, save):
        super().__init__()
        self.events = events
        window = events.size.pipe(
            rmap(lambda s: Rect(0, 0, *s))
        )
        style = Style(events.color_scheme, "Monocraft", 15)

        player_group = Group(0, parent=self.foreground)
        bush_group = Group(1, parent=self.foreground)
        enemy_group = Group(2, parent=self.foreground)

        # im folgenden Block können Elemente eingefügt werden. Die Elemente die schon da sind dienen nur als Beispiele
        self.scroll_background = ui_elements.Gif("assets/images/forest.gif", 0, 0, 100, 100, 30, True, self.events, self.batch, self.background)
        self.header = ui_elements.BorderedRectangle("Level 2: Der Wald des Widerstands", 20, 80, 60, 20, self.events.color_scheme, color_scheme.Minecraft, 2, self.events, self.batch, self.foreground)

        enemy_idle_animation = load_enemy_idle()
        bush_animation = load_bush()
        enemy_run_animation = load_enemy_run()

        def level_generator(msg):
            def generate_bush_enemy_positions():
                """
                Generiert positionen von Büschen und Gegnern. Da dieses Level im prinzip ein endlos-scroller ist,
                gibt es unendlich viele positionen, die generiert werden können.
                :return: ein Generator, welcher per next() neue tupel für busch- und Gegnerpositionen liefert.
                """
                curr = 0
                enemy_offset = 200
                inc = 500
                iinc = 10
                while True:
                    yield Rect(curr, -30, 150, 100), Rect(curr + enemy_offset, -10, 100, 130)
                    curr += inc
                    inc += iinc

            # positionen vorgenerieren, da auf diese hier über index zugegriffen werden muss.
            # bitte nicht weiter spielen als 1000 gegner !!
            positions = list(itertools.islice(generate_bush_enemy_positions(), 1000))

            # bereich für spielobjekte. Bildet u.A. den Boden.
            object_area = window.pipe(
                map_inner_perc(0, 9, 100, 91)
            )

            # es ist ein scroller level, hier ist die aktuelle scroll-weite
            scroll = Var(-1500)
            scroll_off = scroll.pipe(
                rmap(lambda o: Rect(-o, 0, 0, 0))
            )

            # Player-Objekt
            # position ändert sich nicht, aber durch bewegen der anderen Objekte im spiel sieht es so aus, als würde sich der Spieler bewegen.
            player_stationary = Rect(100, -10, 130, 130)
            player_pos = Var(player_stationary)
            self.player = ThePlayer(
                pos=player_pos.pipe(combine_offset(object_area)),
                state=Var(ThePlayer.Running(4.0)),
                look_dir=Var(1),
                batch=self.batch,
                group=player_group,
            )

            # hier werden die aktuell angezeigten objekte (busch, gegner) gespeiechert.
            level_objects = []

            def generate_enemies(index):
                bush_pos, enemy_pos = positions[index]

                enemy = StaticActor(
                    enemy_idle_animation,
                    just(enemy_pos).pipe(
                        combine_offset(scroll_off),
                        combine_offset(object_area)
                    ),
                    look_dir=-1,
                    batch=self.batch,
                    group=enemy_group
                )

                bush = StaticActor(
                    bush_animation,
                    just(bush_pos).pipe(
                        combine_offset(scroll_off),
                        combine_offset(object_area),
                    ),
                    batch=self.batch,
                    group=bush_group
                )

                return bush, enemy

            # es werden immer nur 3 (4) gegner und büsche angezeigt.
            generate_ahead = 3

            # generiere ein paar gegner
            for i in range(generate_ahead):
                level_objects.append(generate_enemies(i))

            def rotate_enemies(index):
                """
                Lösche nicht mehr sichtbare gegner und generiere neue voraus.
                """
                level_objects.pop(0)
                level_objects.append(generate_enemies(index + generate_ahead))

            # spielbeginn: spieler kommt angerannt.
            self.player.state.on_next(ThePlayer.Running(5.0))
            yield CompositeDisposable(
                animate(-1500, -player_stationary.x, 4.0, events.update).subscribe(scroll.on_next, on_completed=msg),
            )

            # spieler sitzt nun hinterm busch.
            level_progress = 0
            max_fails = 10
            fails_left = Var(max_fails)
            long_enough = False
            self._subs.add(  # nach 3 minuten wird das level beendet (flag wird auf true gesetzt)
                animate(0, 0, 3 * 60, events.update)
                .subscribe(on_completed=lambda: locals().update(long_enough=True))
            )

            # wie viele versuche noch - Display
            fails_left_display = BorderedLabel(
                fails_left.pipe(rmap(lambda n: f"Verdächtig: {max_fails-n}/{max_fails}")),
                window.pipe(
                    map_inner_perc(35, 70, 30, 5)
                ),
                style.scale_font_size(0.7),
                batch=self.batch,
                group=self.foreground
            )

            ia = InputAnalysis()
            text_provider = textprovider.statistical.StatisticalTextProvider.from_pickle("assets/text_statistics/stats_1.pickle")

            while not long_enough:
                # spieler anhalten, da am busch
                self.player.state.on_next(ThePlayer.Idle())
                self.scroll_background.paused = True

                # inputbox kreieren und positionieren
                current_enemy_pos = positions[level_progress][1]
                box_pos = just(Rect(-30, -20, 200, 50)).pipe(
                    combine_offset(just(current_enemy_pos)),
                    combine_offset(scroll_off),
                    combine_offset(object_area)
                )
                generation_args = textprovider.TextProviderArgs(20, 20 + level_progress * 2, textprovider.Charset.ALPHA)
                text = text_provider.get_text(generation_args)
                inputbox = InputBox(text, box_pos, style.scale_font_size(.7), events, ia, batch=self.batch, group=enemy_group)

                def react_to_input(tt: TextTracker):
                    if tt.is_finished:
                        msg(True)
                    elif not tt.last_input_correct:
                        msg(False)

                # auf spielereingabe fertig warten
                result = yield CompositeDisposable(
                    inputbox.text_tracker.subscribe(react_to_input)
                )

                # fehler zählen
                if not result:
                    # ausrufezeichen über gegner anzeigen
                    fails_left.on_next(fails_left.value - 1)
                    alert_box = just(Rect(40, 100, 40, 60)).pipe(
                        combine_offset(just(current_enemy_pos)),
                        combine_offset(scroll_off),
                        combine_offset(object_area)
                    )
                    alert_box = BorderedLabel(
                        "!",
                        alert_box,
                        style.scale_font_size(2.0),
                        batch=self.batch,
                        group=enemy_group,
                    )
                    yield animate(0, 0, 0.3, events.update).subscribe(on_completed=msg)
                else:
                    alert_box = Disposable()


                # inputbox weg
                inputbox.dispose()


                if fails_left.value == 0:
                    break

                # vorwärts rennen
                self.player.state.on_next(ThePlayer.Running(5.0))
                self.scroll_background.paused = False
                yield CompositeDisposable(
                    animate(
                        positions[level_progress][0].x - player_stationary.x,
                        positions[level_progress+1][0].x - player_stationary.x,
                        1, events.update
                    ).subscribe(scroll.on_next, on_completed=msg)
                )

                rotate_enemies(level_progress)
                alert_box.dispose()

                level_progress += 1


            # wegrennen, sodass die gegner außer sichtweite kommen
            self.player.state.on_next(ThePlayer.Running(5.0))
            self.scroll_background.paused = False
            yield CompositeDisposable(
                animate(
                    positions[level_progress][0].x - player_stationary.x,
                    positions[level_progress + generate_ahead][0].x - player_stationary.x + 1000,
                    3,
                    events.update
                ).subscribe(scroll.on_next, on_completed=msg)
            )

            # stehenbleiben
            self.player.state.on_next(ThePlayer.Idle())
            self.scroll_background.paused = True
            yield CompositeDisposable(
                animate(0, 0, 2, events.update).subscribe(on_completed=msg)
            )

            # umschauen
            self.player.look_dir.on_next(-1)
            yield CompositeDisposable(
                animate(0, 0, 1, events.update).subscribe(on_completed=msg)
            )

            # erschrecken (ausrufezeichen über Maxwell anzeigen)
            alert_box = just(Rect(40, 120, 40, 60)).pipe(
                combine_offset(just(player_stationary)),
                combine_offset(object_area)
            )
            alert_box = BorderedLabel(
                "!",
                alert_box,
                style.scale_font_size(2.0),
                batch=self.batch,
                group=enemy_group,
            )
            yield animate(0, 0, 0.3, events.update).subscribe(on_completed=msg)

            # umschauen
            self.player.look_dir.on_next(1)
            yield CompositeDisposable(
                animate(0, 0, 1, events.update).subscribe(on_completed=msg)
            )
            alert_box.dispose() # Ausrufezeichen geht weg

            # !!WEGRENNEN!
            self.player.state.on_next(ThePlayer.Running(5.0))
            self.scroll_background.paused = False

            # verfolgende gegner erstellen
            enemy_advance = Var(-200)
            enemy1 = StaticActor(
                enemy_run_animation,
                enemy_advance.pipe(
                    rmap(lambda x: Rect(x, 0, 100, 130)),
                    combine_offset(object_area),
                ),
                batch=self.batch,
                group=enemy_group
            )
            enemy2 = StaticActor(
                enemy_run_animation,
                enemy_advance.pipe(
                    rmap(lambda x: Rect(x-200, -10, 100, 130)),
                    combine_offset(object_area),
                ),
                batch=self.batch,
                group=enemy_group
            )

            # fadeout animation
            animation = concat(
                animate(0, 0, 1, events.update, lambda v: (0, 0, 0, int(v))),
                animate(0, 255, 4, events.update, lambda v: (0, 0, 0, int(v))),
            )

            yield CompositeDisposable(
                animate(-200, 3000, 30, events.update).subscribe(enemy_advance.on_next),
                animate(0, 3000, 20, events.update, lambda x: player_stationary.offset((x, 0))).subscribe(player_pos.on_next),
                Rectangle(window, animation, batch=self.batch, group=self.overlay),
                animation.subscribe(on_completed=msg)
            )

            # ergebnisse speichern
            save_run(save, "story_level_2", ia)

            # Lädt Abschluss-Screen, egal ob
            successful = False
            if fails_left.value > 0: successful = True
            self.reload_screen(LevelFinishedScreen.init_fn(save, 2, calculate_points(ia), successful))  # Abschlussbildschirm des Levels (Save, next_level, Punkte, Erfolgreich)

        self.machine = LevelMachine(level_generator)

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