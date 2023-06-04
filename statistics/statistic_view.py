import pyglet
import pyglet.window.key
import io
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.ticker as ticker
from pyglet import shapes
from random import randint
from events import Events, Event, Var, Disposable
import ui_elements
import color_scheme
import math
import main_controller


class CharView:
    char_name = ""

    def change_char(self, text):
        self.char_name = text

    def get_char(self):
        return self.char_name


class GameSaveInfo:
    current_game_save = ''

    def set_current_game_save(self, save):
        self.current_game_save = save

    def get_current_game_save(self):
        return self.current_game_save


def roundup_to_100(x):
    return int(math.ceil(x / 100.0)) * 100


def roundup_to_10(x):
    return int(math.ceil(x / 10.0)) * 10


def roundup_to_1(x):
    return int(math.ceil(x / 1.0)) * 1


def get_highest_value_from_array(sample_array):
    x = 0
    for data in sample_array:
        if x == 0:
            x = data
        elif x < data:
            x = data
    return x


def get_yaxis_limit(value1, value2):

    if (value1 <= 1) and (value2 <= 1):
        if value1 > value2:
            rounded_value = roundup_to_1(value1)
            return [rounded_value + 0.1, rounded_value / 10]
        elif value1 < value2:
            rounded_value = roundup_to_1(value2)
            return [rounded_value + 0.1, rounded_value / 10]
        else:
            rounded_value = roundup_to_1(value1)
            return [rounded_value + 0.1, rounded_value / 10]
    elif(value1 <= 10) and (value2 <= 10):
        if value1 > value2:
            rounded_value = roundup_to_10(value1)
            return [rounded_value + 0.1, rounded_value / 10]
        elif value1 < value2:
            rounded_value = roundup_to_10(value2)
            return [rounded_value + 0.1, rounded_value / 10]
        else:
            rounded_value = roundup_to_10(value1)
            return [rounded_value + 0.1, rounded_value / 10]
    else:
        if value1 > value2:
            rounded_value = roundup_to_100(value1)
            return [rounded_value + 0.1, rounded_value / 10]
        elif value1 < value2:
            rounded_value = roundup_to_100(value2)
            return [rounded_value + 0.1, rounded_value / 10]
        else:
            rounded_value = roundup_to_100(value1)
            return [rounded_value + 0.1, rounded_value / 10]


def render_figure(fig):
    fig.patch.set_facecolor('xkcd:black')
    fig.subplots_adjust(left=0.1,
                        bottom=0.07,
                        right=0.9,
                        top=0.87,
                        wspace=0.6,
                        hspace=0.4)
    canvas = FigureCanvasAgg(fig)
    data, (w, h) = canvas.print_to_buffer()
    return pyglet.image.ImageData(w, h, "RGBA", data, -4 * w)


def update_image(fig, image):
    # Hier kannst du die gewünschten Änderungen am Bild vornehmen, z.B.:
    image.blit_into(render_figure(fig), 0, 0, 0)


def draw_accuracy_chart(fig, avg_accuracy, current_game_accuracy, char_to_analyse):
    name_of_bars = ['Durchschnittlich', 'letztes Spiel']
    accuracy = [avg_accuracy, current_game_accuracy]
    x = np.arange(len(name_of_bars))
    ax = fig.add_subplot(2, 3, (1, 1))
    ax.bar(x, accuracy, color='#34C7FF', width=0.6, align='center')
    ax.set_title('Genauigkeit des Char: ' + char_to_analyse, color='#de8a1b', fontname='Arial', fontsize=17)
    ax.set_ylabel('Genauigkeit in %', fontname='Arial', fontsize=17)
    ax.set_yticks(np.arange(0, 100.1, 10))
    ax.set_xticks(x)
    ax.set_xticklabels(name_of_bars)
    ax.bar_label(ax.containers[0], label_type='center', color='k', fontsize=17)
    ax.xaxis.set_tick_params(labelsize='large')
    ax.yaxis.set_tick_params(labelsize='large')
    ax.set_facecolor('xkcd:black')
    ax.xaxis.label.set_color('yellow')  # setting up X-axis label color to yellow
    ax.yaxis.label.set_color('white')  # setting up Y-axis label color to blue

    ax.tick_params(axis='x', colors='white', width=3)  # setting up X-axis tick color to red
    ax.tick_params(axis='y', colors='#A4A4A4', width=3)  # setting up Y-axis tick color to black
    ax.spines['left'].set_color('#646464')  # setting up Y-axis tick color to red
    ax.spines['bottom'].set_color('#646464')  # setting up above X-axis tick color to red
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(3)
    ax.spines['bottom'].set_linewidth(3)
    for tick in ax.get_xticklabels():
        tick.set_fontname("Arial")
        tick.set_fontsize(15)


def draw_char_pressed_chart(fig, occurance_in_Game, typed_by_user, char_to_analyse):
    name_of_bars = ['Vorgekommen', 'wirklich gedrückt']
    appearance_of_char = [occurance_in_Game, typed_by_user]
    x = np.arange(len(name_of_bars))
    ax = fig.add_subplot(2, 3, 2)
    ax.bar(x, appearance_of_char, color='#FFC712', width=0.6, align='center')
    ax.set_title('Häufigkeit Char: ' + char_to_analyse, color='#de8a1b', fontname='Arial', fontsize=17)
    ax.set_ylabel('Anzahl des Char', fontname='Arial', fontsize=17)
    ax.set_yticks(np.arange(0, get_yaxis_limit(occurance_in_Game, typed_by_user or 10)[0],
                            get_yaxis_limit(occurance_in_Game, typed_by_user or 10)[1]))
    ax.set_xticks(x)
    ax.set_xticklabels(name_of_bars)
    ax.bar_label(ax.containers[0], label_type='center', color='k', fontsize=17)
    ax.xaxis.set_tick_params(labelsize='large')
    ax.yaxis.set_tick_params(labelsize='large')
    ax.set_facecolor('xkcd:black')
    ax.xaxis.label.set_color('yellow')  # setting up X-axis label color to yellow
    ax.yaxis.label.set_color('white')  # setting up Y-axis label color to blue

    ax.tick_params(axis='x', colors='white', width=3)  # setting up X-axis tick color to red
    ax.tick_params(axis='y', colors='#A4A4A4', width=3)  # setting up Y-axis tick color to black
    ax.spines['left'].set_color('#646464')  # setting up Y-axis tick color to red
    ax.spines['bottom'].set_color('#646464')  # setting up above X-axis tick color to red
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(3)
    ax.spines['bottom'].set_linewidth(3)
    for tick in ax.get_xticklabels():
        tick.set_fontname("Arial")
        tick.set_fontsize(15)


def draw_time_per_char_chart(fig, avg_time, new_time, char_to_analyse):
    name_of_bars = ['Durchschnittlich', 'letztes Spiel']
    appearance_of_char = [avg_time, new_time]
    x = np.arange(len(name_of_bars))
    ax = fig.add_subplot(2, 3, 3)
    ax.bar(x, appearance_of_char, color='#FF55AA', width=0.6, align='center')
    ax.set_title('Zeit zum drücken des Char: ' + char_to_analyse, color='#de8a1b', fontname='Arial', fontsize=17)
    ax.set_ylabel('Zeit in ms', fontname='Arial', fontsize=17)
    ax.set_yticks(np.arange(0, get_yaxis_limit(avg_time, new_time or 100)[0],
                            get_yaxis_limit(avg_time, new_time or 100)[1]))
    ax.set_xticks(x)
    ax.set_xticklabels(name_of_bars)
    ax.bar_label(ax.containers[0], label_type='center', color='k', fontsize=17)
    ax.set_facecolor('xkcd:black')
    ax.xaxis.label.set_color('yellow')  # setting up X-axis label color to yellow
    ax.yaxis.label.set_color('white')  # setting up Y-axis label color to blue
    ax.xaxis.set_tick_params(labelsize='large')
    ax.yaxis.set_tick_params(labelsize='large')
    ax.tick_params(axis='x', colors='white', width=3)  # setting up X-axis tick color to red
    ax.tick_params(axis='y', colors='#A4A4A4', width=3)  # setting up Y-axis tick color to black
    ax.spines['left'].set_color('#646464')  # setting up Y-axis tick color to red
    ax.spines['bottom'].set_color('#646464')  # setting up above X-axis tick color to red
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(3)
    ax.spines['bottom'].set_linewidth(3)
    for tick in ax.get_xticklabels():
        tick.set_fontname("Arial")
        tick.set_fontsize(15)


def bigu_graphu(fig, count_array, data_array1, data_array2, char_to_analyse):
    y = count_array
    data1 = data_array1
    data2 = data_array2
    ax = fig.add_subplot(2, 1, 2)
    if len(y) < 6:
        ax.plot(y, data1, color='#FF55AA', linestyle='dashed', linewidth=3, marker='o',
                markerfacecolor='#FF55AA', markersize=15, label="Ø Zeit")
        ax.plot(y, data2, color='#34C7FF', linestyle='dashed', linewidth=3, marker='o',
                markerfacecolor='#34C7FF', markersize=15, label="Ø Genauigkeit")
    else:
        ax.plot(y, data1, color='#FF55AA', linestyle='dashed', linewidth=3, marker='o',
                markerfacecolor='#FF55AA', markersize=1, label="Ø Zeit")
        ax.plot(y, data2, color='#34C7FF', linestyle='dashed', linewidth=3, marker='o',
                markerfacecolor='#34C7FF', markersize=1, label="Ø Genauigkeit")
    ax.set_title('Zeitlicher Fortschritt des Char: ' + char_to_analyse, color='#de8a1b', fontname='Arial', fontsize=17)
    ax.set_xlabel('Anzahl der Spiele: ' + str(len(y)), fontname='Arial', fontsize=17)#'Characters'
    ax.set_ylabel('Zeit in ms', fontname='Arial', fontsize=17)
    ax.set_yticks(np.arange(0, get_yaxis_limit(get_highest_value_from_array(data1 + data2), 0)[0] or 100,
                  get_yaxis_limit(get_highest_value_from_array(data1 + data2), 0)[1] or 100))
    ax.set_xticks(np.arange(0, len(y)+2.1))
    # Text an dem Graphen
    # ax.text(y[-1]+0.1, data1[-1]-0.2, 'December', style='normal', color='green', fontsize=17)

    ax.legend(frameon=False, framealpha=0.8, bbox_to_anchor=(1.05, 1), labelcolor='linecolor', fontsize=15, loc=1)
    # ncol = 2,facecolor='k', labelcolor='w'

    ax.set_facecolor('xkcd:black')
    ax.xaxis.label.set_color('white')  # setting up X-axis label color to yellow
    ax.yaxis.label.set_color('white')  # setting up Y-axis label color to blue

    ax.xaxis.set_tick_params(labelsize='large')
    ax.yaxis.set_tick_params(labelsize='large')
    ax.tick_params(axis='x', colors='#A4A4A4', width=3)  # setting up X-axis tick color to red
    ax.tick_params(axis='y', colors='#A4A4A4', width=3)  # setting up Y-axis tick color to black
    ax.spines['left'].set_color('#646464')  # setting up Y-axis tick color to red
    ax.spines['bottom'].set_color('#646464')  # setting up above X-axis tick color to red
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(3)
    ax.spines['bottom'].set_linewidth(3)

    for tick in ax.get_xticklabels():
        tick.set_fontname("Arial")
        tick.set_fontsize(15)


def draw_head_box(display_char, events, batch):
    return ui_elements.BorderedRectangle('Statistics for the char: ' + display_char, 27, 93, 46, 7,
                                         color_scheme.BlackWhite,
                                         color_scheme.Minecraft, 3, events, batch=batch)
