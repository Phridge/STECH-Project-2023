import pyglet
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


def roundup(x):
    return int(math.ceil(x / 100.0)) * 100


def get_yaxis_limit(value1, value2):
    if value1 > value2:
        rounded_value = roundup(value1)
        return [rounded_value + 0.1, rounded_value / 10]
    elif value1 < value2:
        rounded_value = roundup(value2)
        return [rounded_value + 0.1, rounded_value / 10]
    else:
        rounded_value = roundup(value1)
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


def draw_accuracy_chart(fig, avg_accuracy, current_game_accuracy):
    name_of_bars = ['in Average', 'in this Game']
    accuracy = [avg_accuracy, current_game_accuracy]
    x = np.arange(len(name_of_bars))
    ax = fig.add_subplot(2, 3, (1, 1))
    ax.bar(x, accuracy, color='#34C7FF', width=0.6, align='center')
    ax.set_title('Accuracy of the Char', color='pink', fontname='Arial', fontsize=17)
    ax.set_ylabel('Accuracy in %', fontname='Arial', fontsize=17)
    ax.set_yticks(np.arange(0, 100.1, 10))
    ax.set_xticks(x)
    ax.set_xticklabels(name_of_bars)
    ax.bar_label(ax.containers[0], label_type='center', color='k')
    ax.xaxis.set_tick_params(labelsize='large')
    ax.yaxis.set_tick_params(labelsize='large')
    ax.set_facecolor('xkcd:black')
    ax.xaxis.label.set_color('yellow')  # setting up X-axis label color to yellow
    ax.yaxis.label.set_color('blue')  # setting up Y-axis label color to blue

    ax.tick_params(axis='x', colors='red', width=3)  # setting up X-axis tick color to red
    ax.tick_params(axis='y', colors='#CC5BA4', width=3)  # setting up Y-axis tick color to black
    ax.spines['left'].set_color('red')  # setting up Y-axis tick color to red
    ax.spines['bottom'].set_color('red')  # setting up above X-axis tick color to red
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(3)
    ax.spines['bottom'].set_linewidth(3)
    for tick in ax.get_xticklabels():
        tick.set_fontname("Arial")
        tick.set_fontsize(15)


def draw_char_pressed_chart(fig, occurance_in_Game, typed_by_user):
    name_of_bars = ['appeared in Game', 'actually pressed']
    appearance_of_char = [occurance_in_Game, typed_by_user]
    x = np.arange(len(name_of_bars))
    ax = fig.add_subplot(2, 3, 2)
    ax.bar(x, appearance_of_char, color='#FFC712', width=0.6, align='center')
    ax.set_title('Appearance of the Char', color='pink', fontname='Arial', fontsize=17)
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
    ax.yaxis.label.set_color('blue')  # setting up Y-axis label color to blue

    ax.tick_params(axis='x', colors='red', width=3)  # setting up X-axis tick color to red
    ax.tick_params(axis='y', colors='#CC5BA4', width=3)  # setting up Y-axis tick color to black
    ax.spines['left'].set_color('red')  # setting up Y-axis tick color to red
    ax.spines['bottom'].set_color('red')  # setting up above X-axis tick color to red
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(3)
    ax.spines['bottom'].set_linewidth(3)
    for tick in ax.get_xticklabels():
        tick.set_fontname("Arial")
        tick.set_fontsize(15)


def draw_time_per_char_chart(fig, avg_time, new_time):
    name_of_bars = ['in average', 'in this Game']
    appearance_of_char = [avg_time, new_time]
    x = np.arange(len(name_of_bars))
    ax = fig.add_subplot(2, 3, 3)
    ax.bar(x, appearance_of_char, color='#D2FF12', width=0.6, align='center')
    ax.set_title('Time to press the Char', color='pink', fontname='Arial', fontsize=17)
    ax.set_ylabel('time in ms', fontname='Arial', fontsize=17)
    ax.set_yticks(np.arange(0, get_yaxis_limit(avg_time, new_time)[0], get_yaxis_limit(avg_time, new_time)[1]))
    ax.set_xticks(x)
    ax.set_xticklabels(name_of_bars)
    ax.bar_label(ax.containers[0], label_type='center', color='k')
    ax.set_facecolor('xkcd:black')
    ax.xaxis.label.set_color('yellow')  # setting up X-axis label color to yellow
    ax.yaxis.label.set_color('blue')  # setting up Y-axis label color to blue
    ax.xaxis.set_tick_params(labelsize='large')
    ax.yaxis.set_tick_params(labelsize='large')
    ax.tick_params(axis='x', colors='red', width=3)  # setting up X-axis tick color to red
    ax.tick_params(axis='y', colors='#CC5BA4', width=3)  # setting up Y-axis tick color to black
    ax.spines['left'].set_color('red')  # setting up Y-axis tick color to red
    ax.spines['bottom'].set_color('red')  # setting up above X-axis tick color to red
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(3)
    ax.spines['bottom'].set_linewidth(3)
    for tick in ax.get_xticklabels():
        tick.set_fontname("Arial")
        tick.set_fontsize(15)


def bigu_graphu(fig):
    y = [1, 2, 3, 4, 5, 6]
    data1 = [1, 7.5, 3, 7, 5, 4]
    data2 = [5, 1, 2, 3, 6.5, 2]
    data3 = [7.7, 2, 3, 6, 7.9, 0.5]
    ax = fig.add_subplot(2, 1, 2)
    ax.plot(y, data1, color='green', linestyle='dashed', linewidth=3, marker='o',
            markerfacecolor='blue', markersize=12, label="avg Time")
    ax.plot(y, data2, color='blue', linestyle='dashed', linewidth=3, marker='o',
            markerfacecolor='green', markersize=12, label="avg Accuracy")
    ax.plot(y, data3, color='red', linestyle='dashed', linewidth=3, marker='o',
            markerfacecolor='purple', markersize=12, label="avg Nom Nom")
    ax.set_title('Stats for all Chars', color='pink', fontname='Arial', fontsize=17)
    ax.set_ylabel('Text ?xD', fontname='Arial', fontsize=17)
    ax.set_ylim(0, 8)
    ax.set_xlim(0, 8)
    #Text an dem Graphen
    #ax.text(y[-1]+0.1, data1[-1]-0.2, 'December', style='normal', color='green', fontsize=17)

    ax.legend(frameon=False, framealpha=0.8, bbox_to_anchor =(1, 1), labelcolor='linecolor', fontsize=15, loc=1)
    #ncol = 2,facecolor='k', labelcolor='w'

    ax.set_facecolor('xkcd:black')
    ax.xaxis.label.set_color('yellow')  # setting up X-axis label color to yellow
    ax.yaxis.label.set_color('blue')  # setting up Y-axis label color to blue
    ax.xaxis.set_tick_params(labelsize='large')
    ax.yaxis.set_tick_params(labelsize='large')
    ax.tick_params(axis='x', colors='red', width=3)  # setting up X-axis tick color to red
    ax.tick_params(axis='y', colors='#CC5BA4', width=3)  # setting up Y-axis tick color to black

    ax.xaxis.set_tick_params(labelsize='large')
    ax.yaxis.set_tick_params(labelsize='large')
    ax.tick_params(axis='x', colors='red', width=3)  # setting up X-axis tick color to red
    ax.tick_params(axis='y', colors='#CC5BA4', width=3)  # setting up Y-axis tick color to black
    ax.spines['left'].set_color('red')  # setting up Y-axis tick color to red
    ax.spines['bottom'].set_color('red')  # setting up above X-axis tick color to red
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(3)
    ax.spines['bottom'].set_linewidth(3)

    for tick in ax.get_xticklabels():
        tick.set_fontname("Arial")
        tick.set_fontsize(15)


# Setting up windows using Pyglet
window = pyglet.window.Window(width=1280, height=720)
dpi_res = min(window.width, window.height) / 10
fig = Figure((window.width / dpi_res, window.height / dpi_res), dpi=dpi_res)
batch = pyglet.graphics.Batch()

events = Events(
    size=Var((window.width, window.height))
)

# Using the draw-figure functionality to render our image:
draw_accuracy_chart(fig, 98.6, 37.5)
draw_char_pressed_chart(fig, 378, 820)
draw_time_per_char_chart(fig, 997, 222)
bigu_graphu(fig)
image = render_figure(fig)
center_line = shapes.Line(1280 * 0, 720 * 0.45, 1280 * 1, 720 * 0.45, 5, color=(255, 255, 255), batch=batch)
# x,y,w,h in % der gesamten Bildschirmgröße. Schriftgröße einfach testen, funktioniert nur mit Integer :(
top_box = ui_elements.BorderedRectangle('Statistics for the char: c', 35, 93, 30, 7, color_scheme.BlackWhite,
                                        color_scheme.Minecraft, 4, events, batch=batch)


@window.event
def on_draw():
    window.clear()
    image.blit(0, 0)
    batch.draw()


# Runner code
pyglet.app.run()
