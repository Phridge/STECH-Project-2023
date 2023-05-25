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


def render_figure(fig):
    fig.patch.set_facecolor('xkcd:black')
    canvas = FigureCanvasAgg(fig)
    data, (w, h) = canvas.print_to_buffer()
    return pyglet.image.ImageData(w, h, "RGBA", data, -4 * w)


def draw_accuracy_chart(fig):
    name_of_bars = ['in Average', 'in this Game']
    accuracy = [98.1, 68.7]
    x = np.arange(len(name_of_bars))
    ax = fig.add_subplot(2, 3, (1, 1))
    ax.bar(x, accuracy, color='#34C7FF', width=0.6, align='center')
    ax.set_title('Accuracy of the Char: c', color='pink', fontsize=17)
    ax.set_ylabel('Accuracy in %', fontsize=17)
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


def draw_char_pressed_chart(fig):
    name_of_bars = ['appeared in Game', 'actually pressed']
    appearance_of_char = [112, 169]
    x = np.arange(len(name_of_bars))
    ax = fig.add_subplot(2, 3, 2)
    ax.bar(x, appearance_of_char, color='#FFC712', width=0.6, align='center')
    ax.set_title('Appearance of the Char: c', color='pink', fontsize=17)
    ax.set_ylabel('Count of the Char', fontsize=17)
    ax.set_yticks(np.arange(0, 201, 25))
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


def draw_time_per_char_chart(fig):
    name_of_bars = ['in average', 'in this Game']
    appearance_of_char = [269, 420]
    x = np.arange(len(name_of_bars))
    ax = fig.add_subplot(2, 3, 3)
    ax.bar(x, appearance_of_char, color='#D2FF12', width=0.6, align='center')
    ax.set_title('Time to press the Char: c', color='pink', fontsize=17)
    ax.set_ylabel('time in ms', fontsize=17)
    ax.set_yticks(np.arange(0, 501, 50))
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


# Setting up windows using Pyglet
window = pyglet.window.Window(width=1280, height=720)
dpi_res = min(window.width, window.height) / 10
fig = Figure((window.width / dpi_res, window.height / dpi_res), dpi=dpi_res)
batch = pyglet.graphics.Batch()

events = Events(
            size=Var((window.width, window.height))
        )

# Using the draw-figure functionality to render our image:
draw_accuracy_chart(fig)
draw_char_pressed_chart(fig)
draw_time_per_char_chart(fig)
image = render_figure(fig)
center_line = shapes.Line(1280 * 0, 720 * 0.45, 1280 * 1, 720 * 0.45, 5, color=(255, 255, 255), batch=batch)
# x,y,w,h in % der gesamten Bildschirmgröße. Schriftgröße einfach testen, funktioniert nur mit Integer :(
top_box = ui_elements.BorderedRectangle('Statistics for the char: c', 35, 93, 30, 7, color_scheme.BlackWhite, color_scheme.Arial, 5, events, batch=batch)


@window.event
def on_draw():
    window.clear()
    image.blit(0, 0)
    batch.draw()


# Runner code
pyglet.app.run()
