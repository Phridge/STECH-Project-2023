import pyglet
# Erweitert die Pyglet-Klassen, um Daraus Buttons, Banner und Formen zu machen


class BorderedRectangleButton(pyglet.shapes.BorderedRectangle): #Pyglet Rectangle wird erweitert um auszugeben wann gehovert und geklickt wird
    def __init__(self, text, x, y, width, height, color_scheme, font_scheme, events, batch=None, group=None):
        pyglet.shapes.BorderedRectangle.__init__(self, x, y, width, height, font_scheme.border_thickness, color_scheme.color, color_scheme.border_color, batch=batch, group=None)
        self.label = pyglet.text.Label(text, batch=batch, font_name="Arial", font_size=12, anchor_x="center", anchor_y="center", x=x+width//2, y=y+height//2)

        def is_hovered(data):
            mouse_x, mouse_y = data
            if x <= int(mouse_x) <= x+width and y <= int(mouse_y) <= y+height:
                self.color = color_scheme.hover_color
                self.border_color = color_scheme.hover_border_color
                self.label.color = color_scheme.hover_text_color
                return True
            else:
                self.color = color_scheme.color
                self.border_color = color_scheme.border_color
                self.label.color = color_scheme.text_color
                return False

        def button_clicked(data):
            pass
            mouse_state, mouse_x, mouse_y, button = data
            if mouse_state is True and button == 1 and x <= int(mouse_x) <= x+width and y <= int(mouse_y) <= y+height:
                self.color = color_scheme.click_color
                self.border_color = color_scheme.click_border_color
                self.label.color = color_scheme.click_text_color
                return True
            else:
                is_hovered((mouse_x, mouse_y))
                return False

        events.mouse.subscribe(is_hovered)
        events.mouse_button.subscribe(button_clicked)

