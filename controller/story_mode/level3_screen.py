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
from controller.actors import Player, ThePlayer, combine_offset, StaticActor
from reactivex import Observable, just, concat
from reactivex.operators import combine_latest, map as rmap, share, starmap, scan, filter as rfilter, do_action

from controller.inputbox import InputBox
from controller.story_mode import Level, LevelMachine, load_enemy_run, animate, load_enemy_barrel_run

from events import Event, Var
from input_tracker import InputAnalysis
from ui_elements_ex import Rect, Style, map_inner_perc, BorderedLabel, Rectangle


def linear_map(v, lo1, hi1, lo2, hi2):
    return  ((v - lo1) / (hi1 - lo1)) * (hi2 - lo2) + lo2

def lerp(v, lo, hi):
    return hi * v + (1 - v) * lo

class Level3Screen(Level):
    def __init__(self, events, save):
        super().__init__()
        self.events = events
        window = events.size.pipe(
            rmap(lambda s: Rect(0, 0, *s))
        )
        style = Style(events.color_scheme, "Monocraft", 15)
        battle_group = Group(0, parent=self.foreground)
        ship_group = Group(1, parent=self.foreground)

        self.gif = ui_elements.Gif("assets/images/city.gif", 0, 0, 100, 100, 5, True, self.events, self.batch,
                                   self.background)

        self.header = ui_elements.BorderedRectangle("Level 3: Die Dampfstadt", 25, 80, 50, 15, self.events.color_scheme, color_scheme.Minecraft, 3.5, self.events, self.batch, self.foreground)

        def level_generator(msg):
            resources = CompositeDisposable()

            object_area = window.pipe(
                map_inner_perc(0, 25, 100, 75)
            )

            player_stationary = Rect(200, 0, 100, 100)
            player_pos = Var(player_stationary)
            p = ThePlayer(
                pos=player_pos.pipe(
                    combine_offset(object_area),
                ),
                state=Var(ThePlayer.Running(5.0)),
                batch=self.batch,
                group=battle_group,
            )
            resources.add(p)

            from textprovider import TextProviderArgs, Charset
            from textprovider.statistical import StatisticalTextProvider
            text_provider = StatisticalTextProvider.from_pickle("assets/text_statistics/stats_1.pickle")

            kill_count = Var(0)
            max_lives = 10
            lives = Var(max_lives)

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

            def enemy_generator(msg, self_disposable):
                strength = random.randint(3, 10)

                enemy_approach_perc = Var(1)
                size_scale = linear_map(strength, 3, 10, 0.7, 2)
                enemy_pos = enemy_approach_perc.pipe(
                    combine_latest(object_area),
                    starmap(lambda x, area: Rect((area.w - player_stationary.x) * x + player_stationary.x + player_stationary.w, area.y, 60 * size_scale, 80 * size_scale))
                )

                enemy = StaticActor(
                    random.choice([load_enemy_run(), load_enemy_barrel_run()]),
                    enemy_pos,
                    look_dir=Var(-1),
                    batch=self.batch,
                    group=battle_group,
                )

                # textgenerierungs args


                min_chars = int(strength/2 * (1 + kill_count.value / 20))
                max_chars = int(strength * (1 + kill_count.value / 20))
                provider_args = TextProviderArgs(min_chars, max_chars, Charset.ALNUM + Charset.EASY_PUNCT)

                # inputbox
                inputbox = InputBox(
                    text_provider.get_text(provider_args),
                    window.pipe(
                        map_inner_perc(30, 3, 67, 17),
                    ),
                    style.scale_font_size(1),
                    events,
                    input_analysis=ia,
                    batch=self.batch,
                    group=self.overlay
                )

                def dispose_inputbox():
                    inputbox.dispose()
                    inputbox_sub.dispose()

                is_finished = False
                enemy_spawn_delay = SingleAssignmentDisposable()

                def enemy_finished():
                    nonlocal is_finished, kill_count

                    is_finished = True
                    kill_count.on_next(kill_count.value + 1)

                    # weg mit der inputbox
                    dispose_inputbox()

                    # neuer gegner nach gegebener zeit
                    def new_enemy():
                        spawn_new_enemy()
                        enemy_spawn_delay.dispose()
                    enemy_spawn_delay.disposable = animate(0, 0, 0.5, events.update).subscribe(on_completed=new_enemy)

                def on_input(tt):
                    if tt.is_finished:
                        enemy_finished()

                inputbox_sub = inputbox.text_tracker.subscribe(on_input)

                def at_player():
                    dispose_inputbox()
                    msg()

                yield CompositeDisposable(
                    animate(1.0, 0.0, strength, events.update)  # gegner zum spieler bewegen
                    .subscribe(enemy_approach_perc.on_next, on_completed=at_player)
                )

                if is_finished:
                    p.state.on_next(p.Attacking(None))
                    attack = animate(0.0, 0.0, 1, events.update)
                    yield CompositeDisposable(
                        attack.subscribe(on_completed=msg)
                    )
                    p.state.on_next(p.Running(5.0))
                else:
                    nonlocal lives
                    lives.on_next(lives.value - 1)

                    p.state.on_next(p.Hurt())
                    enemy.look_dir.on_next(1)

                    def reset():
                        p.state.on_next(p.Running(5.0))
                        if lives.value > 0:
                            spawn_new_enemy()
                        else:
                            all_lives_lost()
                    yield CompositeDisposable(
                        animate(0, 0, 2, events.update).subscribe(on_completed=reset),
                        animate(0.0, -1.0, 5, events.update)
                        .subscribe(enemy_approach_perc.on_next, on_completed=msg)
                    )

                enemy.dispose()
                self_disposable.dispose()

            enemies = CompositeDisposable()

            def spawn_new_enemy():
                remove_handle = Disposable(lambda: enemies.remove(enemy))
                enemy = LevelMachine(lambda msg: enemy_generator(msg, remove_handle))
                enemies.add(enemy)

            spawn_new_enemy()

            def all_lives_lost(): msg()

            yield None

            ship_pos = Event()
            ship = StaticActor(
                pyglet.image.load("assets/images/ship.png"),
                ship_pos,
                batch=self.batch,
                group=ship_group
            )
            resources.add(ship)
            resources.add(ship_pos)

            yield CompositeDisposable(
                animate(0, 1, 4, events.update).pipe(
                    combine_latest(object_area),
                    starmap(lambda p, area: Rect(area.w - 300, lerp(p, area.h, area.y - 20), 700, 500))
                ).subscribe(ship_pos.on_next),
                animate(0, 1, 6, events.update).pipe(
                    do_action(on_completed=msg),
                    combine_latest(object_area),
                    starmap(lambda p, area: Rect(lerp(p, player_stationary.x, area.w), player_stationary.y, player_stationary.w, player_stationary.h))
                ).subscribe(player_pos.on_next),
                enemies,
            )
            yield animate(0, 0, 1, events.update).subscribe(on_completed=msg)
            yield CompositeDisposable(
                Rectangle(window, animate(0, 255, 3, events.update, lambda v: (0, 0, 0, int(v))), batch=self.batch, group=self.overlay),
                animate(1, 0, 3, events.update).pipe(
                    do_action(on_completed=msg),
                    combine_latest(object_area),
                    starmap(lambda p, area: Rect(area.w - 300, lerp(p, area.h, area.y - 20), 700, 500))
                ).subscribe(ship_pos.on_next)
            )


            points = int((ia.correct_char_count / ia.time) ** 2 * 100)

            resources.dispose()


            from controller.level_finished import LevelFinishedScreen
            self.reload_screen(LevelFinishedScreen.init_fn(save, 2, points, True))  # Abschlussbildschirm des Levels (Save, next_level, Punkte, Erfolgreich)

        self.machine = LevelMachine(level_generator)

    def get_view(self):  # Erzeugt den aktuellen View
        return self.batch

    def play_music(self, nextmusic):
        with contextlib.suppress(pygame.error):
            mixer.init()
            mixer.music.load(nextmusic)
            mixer.music.play()
            mixer.music.play(-1)
