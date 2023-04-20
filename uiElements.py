import pyglet

# Erweitert die Pyglet-Klassen, um Daraus Buttons, Banner und Formen zu machen


class BorderedRectangleButton(pyglet.shapes.BorderedRectangle): #Pyglet Rectangle wird erweitert um auszugeben wann gehovert und geklickt wird
    def __init__(self, text, x, y, width, height, border, color, border_color, hover_color, hover_border_color, click_color, click_border_color, events, batch=None, group=None):
        pyglet.shapes.BorderedRectangle.__init__(self, x, y, width, height, border, color, border_color, batch=batch, group=None)
        pyglet.text.Label(text, batch=batch, font_name="Arial", font_size=36, anchor_x="center", anchor_y="center", x=x+width // 2, y=y+height // 2)

        def isHovered(data):
            mouseX, mouseY = data
            if x <= int(mouseX) <= x+width and y <= int(mouseY) <= y+height:
                self.color = hover_color
                self.border_color = hover_border_color
                return True
            else:
                self.color = color
                self.border_color = border_color
                return False

        def buttonClicked(data):
            pass
            mouseState, mouseX, mouseY, button = data
            if mouseState is True and button == 1 and x <= int(mouseX) <= x+width and y <= int(mouseY) <= y+height:
                self.color = click_color
                self.border_color = click_border_color
                return True
            else:
                isHovered((mouseX, mouseY))
                return False

        events.mouse.subscribe(isHovered)
        events.mouse_button.subscribe(buttonClicked)

