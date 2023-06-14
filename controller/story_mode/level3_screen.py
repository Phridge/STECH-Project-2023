import logging
import time
import random

import pyglet
import pygame
from pygame import mixer
import contextlib

from pyglet.graphics import Group

import color_scheme
import ui_elements
from reactivex.subject import Subject
from reactivex.disposable import CompositeDisposable, Disposable, MultipleAssignmentDisposable, \
    SingleAssignmentDisposable
from controller import Screen
from controller.actors import ThePlayer, combine_offset, StaticActor
from reactivex import Observable, just, concat, Observer
from reactivex.operators import combine_latest, map as rmap, share, starmap, scan, filter as rfilter, do_action

from controller.inputbox import InputBox
from controller.story_mode import Level, LevelMachine, load_enemy_run, animate, load_enemy_barrel_run

from events import Event, Var
from input_tracker import InputAnalysis
from ui_elements_ex import Rect, Style, map_inner_perc, BorderedLabel, Rectangle, Button


def linear_map(v, lo1, hi1, lo2, hi2):
    return  ((v - lo1) / (hi1 - lo1)) * (hi2 - lo2) + lo2


def lerp(v, lo, hi):
    return hi * v + (1 - v) * lo


class Level3Screen(Level):
    """
    Level 3 screen.
    """
    def __init__(self, events, save):
        """
        Erstelle einen
        :param events:
        :param save:
        """
        super().__init__(events, save)
        window = self.events.size.pipe(
            rmap(lambda s: Rect(0, 0, *s))
        )
        style = Style(self.events.color_scheme, "Monocraft", 15)

        # zum sortieren von Spielobjekten.
        battle_group = Group(0, parent=self.foreground)  # alle, die im kampf involviert sind
        ship_group = Group(1, parent=self.foreground)  # das luftschiff, muss vorm spielern sein

        # hintergrund
        self.gif = ui_elements.Gif("assets/images/city.gif", 0, 0, 100, 100, 5, True, self.events, self.batch, self.background)

        # header
        self.header = ui_elements.BorderedRectangle("Level 3: Die Dampfstadt", 25, 80, 50, 15, self.events.color_scheme, color_scheme.Minecraft, 3.5, self.events, self.batch, self.foreground)
        self.play_music()

        def level_generator(msg):
            """
            Generiert das dritte Level und die komplette Aktions-Abfolge
            """
            # alle resourcen werden hier gesammelt um am ende freigelassen.
            resources = CompositeDisposable()

            # region, in dem die acteure wie spieler und gegner sich befinden
            object_area = window.pipe(
                map_inner_perc(0, 25, 100, 75)
            )

            # da, wo der spieler in der object_area sich befindet. dort steht er und macht sein ding.
            player_stationary = Rect(200, 0, 100, 100)
            # spielerposition, kann animiert werden
            player_pos = Var(player_stationary)
            p = ThePlayer(
                pos=player_pos.pipe(
                    combine_offset(object_area),
                ),
                state=Var(ThePlayer.Running(5.0)),  # am anfang rennt der spieler
                batch=self.batch,
                group=battle_group,
            )
            resources.add(p)

            from textprovider import TextProviderArgs, Charset
            from textprovider.statistical import StatisticalTextProvider
            text_provider = StatisticalTextProvider.from_pickle("assets/text_statistics/stats_1.pickle")

            kill_count = Var(0)  # wie viele kills hat der spieler schon?
            max_lives = 10  # maximale leben des Spielers
            lives = Var(max_lives)  # aktiver counter, wieviele leben er noch hat.

            # anzeige für kills und übrige leben
            fails_left_display = BorderedLabel(
                kill_count.pipe(
                    combine_latest(lives),
                    starmap(lambda kill_count, lives: f"Kills: {kill_count} | Leben: {lives}")),
                window.pipe(
                    map_inner_perc(35, 70, 30, 5)
                ),
                style.scale_font_size(0.7),
                batch=self.batch,
                group=battle_group
            )
            resources.add(fails_left_display)

            ia = InputAnalysis()

            def enemy_generator(msg, dispose_self):
                """
                Generiert die Gegner zufällig.

                Das ist ein Generator, der den Lebensablauf eines Gegners verwaltet. Ein gegner wird zu beginn erstellt und
                an den rechten rand des Spielfeldes gesetzt, dann rennt er geradewegs mit seiner eigenen Geschwindigketi
                auf den Spieler drauf zu. Unterdessen muss "sein" text eingegeben werden. Geschieht das, gilt dieser
                Gegner als besiegt und wird, sobald er am spieler ankommt, zerstört. Wird der TExt nicht rechtzeitig
                eingegeben, schadet dieser Gegner den Spieler, ein Leben wird abgezogen. Danach verschwindet der Gegner
                langsam hinterm Linken Spielfeldrand.
                """

                # zufällig generierte "Stärke".
                # Stärkere Gegner haben längeren Text, laufen auch langsamer, sodass es für jeden Gegner ausgeglichen ist.
                strength = random.randint(3, 10)

                # wie weit er bis hin zum Spieler schon gerannt ist, 0 - 1.
                # dieser anteil wird auf die Distanz zwischen Spieler und Rechter Rand gemappt (per lerp).
                enemy_approach_perc = Var(1)
                size_scale = linear_map(strength, 3, 10, 0.7, 2)  # stärke zu Größe des bildes
                enemy_pos = enemy_approach_perc.pipe(
                    combine_latest(object_area),
                    starmap(lambda x, area: Rect((area.w - player_stationary.x) * x + player_stationary.x + player_stationary.w, area.y, 60 * size_scale, 80 * size_scale))
                )

                # Das aussehen des Gegners ist zufällig gewählt zwischen zwei verschiedenen Animationen.
                enemy = StaticActor(
                    random.choice([load_enemy_run(), load_enemy_barrel_run()]),
                    enemy_pos,
                    look_dir=Var(-1),
                    batch=self.batch,
                    group=battle_group,
                )

                # Textgenerationsargumente.
                # die mögliche mindest- und maximalanzahl der Generierten Buchstaben erhöht sich immer weiter,
                # sodass gegner mit steigendem killcount immer stärker werden.
                min_chars = int(strength/2 * (1 + kill_count.value / 20))
                max_chars = int(strength * (1 + kill_count.value / 20))
                provider_args = TextProviderArgs(min_chars, max_chars, Charset.ALNUM + Charset.EASY_PUNCT)

                # inputbox
                # ist immer an der gleichen stelle, da sich bewegende Inputboxen schlecht lesbar sind.
                inputbox = InputBox(
                    text_provider.get_text(provider_args),
                    window.pipe(
                        map_inner_perc(30, 3, 67, 17),
                    ),
                    style.scale_font_size(1),
                    self.events,
                    input_analysis=ia,
                    batch=self.batch,
                    group=self.overlay
                )

                def dispose_inputbox():
                    """
                    löscht die Inputbox, wenn der Gegner beim Spieler ist oder der Text fertig eingegeben ist
                    """
                    inputbox.dispose()
                    inputbox_sub.dispose()

                is_finished = False  # wurde dieser Gegner besiegt?
                # Disposable, um eine pause einzulegen zwischen gegner besiegt und neuer gegner erscheint
                enemy_spawn_delay = SingleAssignmentDisposable()

                def enemy_finished():
                    """
                    Wenn der Gegner beim Spieler ist oder getötet wurde, wird ein neuer Gegner gespawnt
                    :return:
                    """
                    nonlocal is_finished, kill_count

                    is_finished = True
                    # killcount erhöhen
                    kill_count.on_next(kill_count.value + 1)

                    # weg mit der inputbox
                    dispose_inputbox()

                    # neuer gegner nach gegebener zeit
                    def new_enemy():
                        """
                        Erstellt neuen Gegner und setzt das Spawn-Delay zurück
                        """
                        spawn_new_enemy()
                        enemy_spawn_delay.dispose()
                    enemy_spawn_delay.disposable = animate(0, 0, 0.5, self.events.update).subscribe(on_completed=new_enemy)

                def on_input(tt):
                    """
                    Testet, ob die InputBox abgetippt ist. Wenn ja, wird der aktuelle Gegner getötet
                    :param tt: Text der InputBox
                    """
                    if tt.is_finished:
                        enemy_finished()

                # auf änderun in der INputbox hören
                inputbox_sub = inputbox.text_tracker.subscribe(on_input)

                def at_player():
                    dispose_inputbox()
                    msg()

                # "Laufe-zum-Spieler"-Zustand. Nächster zustand, wenn beim Spieler (laufanimation fertig)
                yield CompositeDisposable(
                    animate(1.0, 0.0, strength, self.events.update)  # gegner zum spieler bewegen
                    .subscribe(enemy_approach_perc.on_next, on_completed=at_player)
                )


                if is_finished:
                    # wenn dieser Gegner gekillt wurde, den Spieler auf attackieren setzen
                    p.state.on_next(p.Attacking(None))
                    # eine sekunde lang attackieren
                    attack = animate(0.0, 0.0, 1, self.events.update)
                    yield CompositeDisposable(
                        attack.subscribe(on_completed=msg)
                    )
                    # spieler wieder auf rennend setzen
                    p.state.on_next(p.Running(5.0))
                else:
                    nonlocal lives
                    # spieler aua
                    lives.on_next(lives.value - 1)

                    p.state.on_next(p.Hurt())

                    # drehe den Gegner um, sodass es aussieht, als würde Maxwell schneller als der Gegner rennen
                    enemy.look_dir.on_next(1)

                    def reset():
                        """
                        setze den Spieler wieder auf rennend und erschaffe einen Neuen gegner, falls noch leben da sind.
                        """
                        p.state.on_next(p.Running(5.0))
                        if lives.value > 0:
                            spawn_new_enemy()
                        else:
                            # unterbreche die neu-Spawn-schleife
                            all_lives_lost()

                    # nach 2 sekunden spieler aua, neuer gegner.
                    # dieser Gegner wird nach 5 sekunden gelöscht
                    yield CompositeDisposable(
                        animate(0, 0, 2, self.events.update).subscribe(on_completed=reset),
                        animate(0.0, -1.0, 5, self.events.update)
                        .subscribe(enemy_approach_perc.on_next, on_completed=msg)
                    )

                # gegner ACtor löschen
                enemy.dispose()
                # und diesen callback auch, sodass dieser Gegner aus der Liste der Gegner gelöscht und disposed wird
                dispose_self()

            # liste der Gegner.
            # Löschen sich gegner selbständig aus dieser Liste, werden sie disposed.
            enemies = CompositeDisposable()

            def spawn_new_enemy():
                """
                Erstellt einen neuen Gegner und fügt diesen in die Gegner in die Gegnerliste ein
                """
                # dieser callback entfernt den gegner
                remove_handle = lambda: enemies.remove(enemy)
                enemy = LevelMachine(lambda msg: enemy_generator(msg, remove_handle))
                enemies.add(enemy)

            # einen initialen Gegner losschicken.
            spawn_new_enemy()

            def all_lives_lost():
                """Den nächsten Levelzustand (nicht den eines Gegners!) aufrufen."""
                msg()

            yield None

            # jetzt rennt der Spieler an den Rechten rand des Levels, wo ein Schiff vom Himmel herabfliegt
            # maxwell wird dann von diesem abgeholt, das Schiff bewegt sich nach oben.

            # schiffsposition zum animieren
            ship_pos = Event()
            ship = StaticActor(
                pyglet.image.load("assets/images/ship.png"),
                ship_pos,
                batch=self.batch,
                group=ship_group
            )
            resources.add(ship)
            resources.add(ship_pos)

            # animationen: Spieler nach rechts, SChiff nach unten
            yield CompositeDisposable(
                animate(0, 1, 4, self.events.update).pipe(
                    combine_latest(object_area),
                    starmap(lambda p, area: Rect(area.w - 300, lerp(p, area.h, area.y - 20), 700, 500))
                ).subscribe(ship_pos.on_next),
                animate(0, 1, 6, self.events.update).pipe(
                    do_action(on_completed=msg),
                    combine_latest(object_area),
                    starmap(lambda p, area: Rect(lerp(p, player_stationary.x, area.w), player_stationary.y, player_stationary.w, player_stationary.h))
                ).subscribe(player_pos.on_next),
                enemies,
            )

            # eine Sekunde lang warten
            yield animate(0, 0, 1, self.events.update).subscribe(on_completed=msg)

            # Schiff nach oben. Spieler wird nicht animiert, ist sowiso nicht sichtbar.
            yield CompositeDisposable(
                Rectangle(window, animate(0, 255, 3, self.events.update, lambda v: (0, 0, 0, int(v))), batch=self.batch, group=self.overlay),
                animate(1, 0, 3, self.events.update).pipe(
                    do_action(on_completed=msg),
                    combine_latest(object_area),
                    starmap(lambda p, area: Rect(area.w - 300, lerp(p, area.h, area.y - 20), 700, 500))
                ).subscribe(ship_pos.on_next)
            )


            # selbsterklärend
            points = int((ia.correct_char_count / ia.time) ** 2 * 100)

            # alle resourcen löschen
            resources.dispose()

            # zum zwischenscreen wechseln.
            from controller.level_finished import LevelFinishedScreen
            self.reload_screen(LevelFinishedScreen.init_fn(save, 2, points, True))  # Abschlussbildschirm des Levels (Save, next_level, Punkte, Erfolgreich)

        # maschine erstellen, los gehts.
        self.machine = LevelMachine(level_generator)

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch

    def play_music(self):
        with contextlib.suppress(pygame.error):
            mixer.init()
            mixer.music.load("assets/sounds/Run.mp3")
            mixer.music.play(-1)
