import pyglet
from reactivex.subject import BehaviorSubject, Subject

class BorderedRectangleButton(pyglet.shapes.BorderedRectangle): #Pyglet Button wird erweitert um auszugeben wann er gehovert und geklickt wird
    def __init__(self, x, y, width, height, border, color, border_color, hover_color, border_hover_color, events, batch=None, group=None):
        pyglet.shapes.BorderedRectangle.__init__(self, x, y, width, height, border, color, border_color, batch=None, group=None)

        def isHovered(data):
            mouseX, mouseY = data
            if int(mouseX) >= x and int(mouseX) <= x+width and int(mouseY) >= y and int(mouseY) <= y+height:
                self.color = hover_color
                self.border_color = border_hover_color
                return True
            else:
                self.color = color
                self.border_color = border_color
                return False

        def buttonClicked(data):
            if isHovered == True and data[0] == True:
                return True
            else:
                return False

        events.mouse.subscribe(isHovered)
        events.mouse_button.subscribe(buttonClicked)
        events.mouse_button.subscribe(buttonClicked)

