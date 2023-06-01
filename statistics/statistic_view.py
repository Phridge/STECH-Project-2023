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
import statistics_controller


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


def get_highest_value_from_array(sample_array):
    x = ''
    for data in sample_array:
        if x == '':
            x = data
        elif x < data:
            x = data
    return x


def get_yaxis_limit(value1, value2):

    if (value1 > 100) and (value2 > 100):
        if value1 > value2:
            rounded_value = roundup_to_100(value1)
            return [rounded_value + 0.1, rounded_value / 10]
        elif value1 < value2:
            rounded_value = roundup_to_100(value2)
            return [rounded_value + 0.1, rounded_value / 10]
        else:
            rounded_value = roundup_to_100(value1)
            return [rounded_value + 0.1, rounded_value / 10]
    else:
        if value1 > value2:
            rounded_value = roundup_to_10(value1)
            return [rounded_value + 0.1, rounded_value / 10]
        elif value1 < value2:
            rounded_value = roundup_to_10(value2)
            return [rounded_value + 0.1, rounded_value / 10]
        else:
            rounded_value = roundup_to_10(value1)
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


def update_image(fig):
    # Hier kannst du die gewünschten Änderungen am Bild vornehmen, z.B.:
    image.blit_into(render_figure(fig), 0, 0, 0)


def draw_accuracy_chart(fig, avg_accuracy, current_game_accuracy, char_to_analyse):
    name_of_bars = ['in Average', 'in this Game']
    accuracy = [avg_accuracy, current_game_accuracy]
    x = np.arange(len(name_of_bars))
    ax = fig.add_subplot(2, 3, (1, 1))
    ax.bar(x, accuracy, color='#34C7FF', width=0.6, align='center')
    ax.set_title('Accuracy of the Char: ' + char_to_analyse, color='#de8a1b', fontname='Arial', fontsize=17)
    ax.set_ylabel('Accuracy in %', fontname='Arial', fontsize=17)
    ax.set_yticks(np.arange(0, 100.1, 10))
    ax.set_xticks(x)
    ax.set_xticklabels(name_of_bars)
    ax.bar_label(ax.containers[0], label_type='center', color='k')
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
    name_of_bars = ['appeared in Game', 'actually pressed']
    appearance_of_char = [occurance_in_Game, typed_by_user]
    x = np.arange(len(name_of_bars))
    ax = fig.add_subplot(2, 3, 2)
    ax.bar(x, appearance_of_char, color='#FFC712', width=0.6, align='center')
    ax.set_title('Appearance of the Char: ' + char_to_analyse, color='#de8a1b', fontname='Arial', fontsize=17)
    ax.set_ylabel('Count of the Char', fontname='Arial', fontsize=17)
    ax.set_yticks(np.arange(0, get_yaxis_limit(occurance_in_Game, typed_by_user)[0],
                            get_yaxis_limit(occurance_in_Game, typed_by_user)[1]))
    ax.set_xticks(x)
    ax.set_xticklabels(name_of_bars)
    ax.bar_label(ax.containers[0], label_type='center', color='k')
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
    name_of_bars = ['in average', 'in this Game']
    appearance_of_char = [avg_time, new_time]
    x = np.arange(len(name_of_bars))
    ax = fig.add_subplot(2, 3, 3)
    ax.bar(x, appearance_of_char, color='#FF55AA', width=0.6, align='center')
    ax.set_title('Time to press the Char: ' + char_to_analyse, color='#de8a1b', fontname='Arial', fontsize=17)
    ax.set_ylabel('time in ms', fontname='Arial', fontsize=17)
    ax.set_yticks(np.arange(0, get_yaxis_limit(avg_time, new_time)[0], get_yaxis_limit(avg_time, new_time)[1]))
    ax.set_xticks(x)
    ax.set_xticklabels(name_of_bars)
    ax.bar_label(ax.containers[0], label_type='center', color='k')
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


def bigu_graphu(fig, data_array1, data_array2, data_array3):
    y = [1, 2, 3, 4, 5, 6,7,8,9,10,11]
    data1 = data_array1
    data2 = data_array2
    data3 = data_array3
    ax = fig.add_subplot(2, 1, 2)
    ax.plot(y, data1, color='#FF55AA', linestyle='dashed', linewidth=3, marker='o',
            markerfacecolor='#FF55AA', markersize=12, label="avg Time")
    ax.plot(y, data2, color='#34C7FF', linestyle='dashed', linewidth=3, marker='o',
            markerfacecolor='#34C7FF', markersize=12, label="avg Accuracy")
    ax.plot(y, data3, color='#FFC712', linestyle='dashed', linewidth=3, marker='o',
            markerfacecolor='#FFC712', markersize=12, label="chars typed")
    ax.set_title('Stats for all Chars', color='#de8a1b', fontname='Arial', fontsize=17)
    ax.set_xlabel('Characters', fontname='Arial', fontsize=17)
    ax.set_ylabel('Values', fontname='Arial', fontsize=17)
    ax.set_yticks(np.arange(0, get_yaxis_limit(get_highest_value_from_array(data1 + data2 + data3), 0)[0],
                  get_yaxis_limit(get_highest_value_from_array(data1 + data2 + data3), 0)[1]))
    ax.set_xticks(np.arange(0, len(y)+2.1))
    # Text an dem Graphen
    # ax.text(y[-1]+0.1, data1[-1]-0.2, 'December', style='normal', color='green', fontsize=17)

    ax.legend(frameon=False, framealpha=0.8, bbox_to_anchor=(1.02, 1), labelcolor='linecolor', fontsize=15, loc=1)
    # ncol = 2,facecolor='k', labelcolor='w'

    ax.set_facecolor('xkcd:black')
    ax.xaxis.label.set_color('white')  # setting up X-axis label color to yellow
    ax.yaxis.label.set_color('white')  # setting up Y-axis label color to blue

    ax.xaxis.set_tick_params(labelsize='large')
    ax.yaxis.set_tick_params(labelsize='large')
    #ax.tick_params(axis='x', colors='#CC5BA4', width=3)  # setting up X-axis tick color to red
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


def draw_head_box(display_char, batch):
    return ui_elements.BorderedRectangle('Statistics for the char: ' + display_char, 35, 93, 30, 7,
                                         color_scheme.BlackWhite,
                                         color_scheme.Minecraft, 4, events, batch=batch)


# Setting up windows using Pyglet
window = pyglet.window.Window(width=1280, height=720)
dpi_res = min(window.width, window.height) / 10
fig = Figure((window.width / dpi_res, window.height / dpi_res), dpi=dpi_res)
batch = pyglet.graphics.Batch()
canvas = {}
image = pyglet.image.create(width=1280, height=720).get_texture()
events = Events(
    size=Var((window.width, window.height))
)

# Instanziiert klassen
current_char = CharView()
current_game_save = GameSaveInfo()

# Zeichnet erste graphen
draw_accuracy_chart(fig, 98.6, 37.5, current_char.get_char())
draw_char_pressed_chart(fig, 378, 820, current_char.get_char())
draw_time_per_char_chart(fig, 997, 222, current_char.get_char())
bigu_graphu(fig,[1, 7.5, 3, 7, 5, 4, 7, 9, 8, 4, 1], [5, 1, 2, 3, 6.5, 2,1,5,6,2,7], [7.7, 2, 3, 6, 7.9, 0.5,1,2,1,1,3])

update_image(fig)
center_line = shapes.Line(1280 * 0, 720 * 0.46, 1280 * 1, 720 * 0.46, 5, color=(100, 100, 100), batch=batch)

# x,y,w,h in % der gesamten Bildschirmgröße. Schriftgröße einfach testen, funktioniert nur mit Integer :(
canvas[1] = draw_head_box('Sample', batch)


# Hier ist noch ein fehler D:
@window.event
def on_draw():
    window.clear()
    image.blit(0, 0)
    batch.draw()


@window.event
def on_text(text):
    current_char.change_char(text)
    print(current_char.get_char())
    canvas[1].label.text = 'Statistics for the char: ' + current_char.get_char()
    fig.clf()
    # graphen zeichnen
    draw_accuracy_chart(fig, 98.6, 37.5, current_char.get_char())
    draw_char_pressed_chart(fig, 378, 820, current_char.get_char())
    draw_time_per_char_chart(fig, 1997, 222, current_char.get_char())
    bigu_graphu(fig,
                [1, 7.5, 3, 7, 5, 4, 1, 7, 3, 2.5, 5],
                [5, 1, 2, 3, 6.5, 2, 9, 1.1, 5, 35, 5],
                [7.7, 2, 3, 6, 7.9, 0.5, 3, 4, 5, 7, 2])
    update_image(fig)


# Runner code
pyglet.app.run()
