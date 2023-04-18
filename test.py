import pyglet
from pyglet.window import key
from reactivex.subject import BehaviorSubject

stuff = BehaviorSubject(None)

window = pyglet.window.Window()

label = pyglet.text.Label("",
                          font_name='Times New Roman',
                          font_size=36,
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center')


def reaction(x):
    label.text = f"Typed {x}" if x else "Press something"


stuff.subscribe(reaction)

# phil war hier
# Martin war hier


@window.event
def on_draw():
    window.clear()
    label.draw()


@window.event
def on_text(text):
    stuff.on_next(text)



pyglet.app.run()
