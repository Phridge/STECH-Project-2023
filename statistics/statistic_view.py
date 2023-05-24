import pyglet
import io
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.ticker as ticker


def render_figure(fig):
    canvas = FigureCanvasAgg(fig)
    data, (w, h) = canvas.print_to_buffer()
    return pyglet.image.ImageData(w, h, "RGBA", data, -4 * w)


def draw_accuracy_chart(fig):
    name_of_bars = ['Average', 'this Game']
    accuracy = [98.1, 68.7]
    x = np.arange(len(name_of_bars))
    ax = fig.add_subplot(2, 3, (1, 1))
    ax.bar(x, accuracy, color='#34C7FF', width=0.6, align='center')
    ax.set_title('Accuracy of the Char: c')
    ax.set_ylabel('Accuracy in %')
    ax.set_yticks(np.arange(0, 100.1, 10))
    ax.set_xticks(x)
    ax.set_xticklabels(name_of_bars)
    ax.bar_label(ax.containers[0], label_type='center')
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(0.5))
    # ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.5))


def draw_char_pressed_chart(fig):
    name_of_bars = ['Average', 'this Game']
    accuracy = [98.1, 68.7]
    x = np.arange(len(name_of_bars))
    ax = fig.add_subplot(2, 3, (1, 1))
    ax.bar(x, accuracy, color='#34C7FF', width=0.6, align='center')
    ax.set_title('Accuracy of the Char: c')
    ax.set_ylabel('Accuracy in %')
    ax.set_yticks(np.arange(0, 100.1, 10))
    ax.set_xticks(x)
    ax.set_xticklabels(name_of_bars)
    ax.bar_label(ax.containers[0], label_type='center')
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(0.5))
    # ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.5))


# Setting up windows using Pyglet
window = pyglet.window.Window(fullscreen=True)
dpi_res = min(window.width, window.height) / 10
fig = Figure((window.width / dpi_res, window.height / dpi_res), dpi=dpi_res)

# Using the draw-figure functionality to render our image:
draw_accuracy_chart(fig)
image = render_figure(fig)


@window.event
def on_draw():
    window.clear()
    image.blit(0, 0)


# Runner code
pyglet.app.run()
