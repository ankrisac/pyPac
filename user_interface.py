class Widget(object):
    def __init__(self):
        self.resize(0, 0, 1, 1)
        self.parent = None

    def apply_fun(self, fun):
        fun(self)
        return self

    def set_parent(self, parent):
        self.parent = parent
        return self

    def resize(self, x1, y1, x2, y2):
        self._pos_1 = PVector(x1, y1)
        self._pos_2 = PVector(x2, y2)
        return self

    def get_width(self): return self._pos_2.x - self._pos_1.x
    def get_height(self): return self._pos_2.y - self._pos_1.y

    def get_absolute_pos(self, pos):
        t_pos = self._pos_1 + PVector(self.get_width() * pos.x, self.get_height() * pos.y)
        return self.parent.get_absolute_pos(t_pos) if self.parent != None else t_pos

    def update(self, event): return self
    def render(self, buffer): return self

class Panel(Widget):
    def __init__(self):
        self._child_widgets = []
        super(Panel, self).__init__()

    def apply_fun(self, fun):
        fun(self)
        for i in self._child_widgets:
            i.apply_fun(fun)

    def push_widget(self, elem):
        self._child_widgets.append(elem.set_parent(self))
        return self
    
    def pop_widget(self):
        return self._child_widgets.pop()

    def clear_widgets(self):
        self._child_widgets = []
        return self

    def set_widget(self, i, elem):
        self._child_widgets[i] = elem
        return self

    def get_widget(self, i): return self._child_widgets[i]

    def update(self, event):
        for i in self._child_widgets:
            i.update(event)
        return self
        
    def render(self, buffer):
        for i in self._child_widgets:
            i.render(buffer)
        return self

class Window(Panel):
    def __init__(self):
        self.font = createFont("Courier New", 50)
        self.set_background(100)

        super(Window, self).__init__()
        self.resize(0, 0, 1, 1)
        
    def set_background(self, col):
        self.background = col

    def update_buffer(self):
        self._image.noSmooth()
        self._image.beginDraw()

        self._image.colorMode(RGB, 100)
        self._image.background(self.background)

        self._image.imageMode(CORNERS)
        self._image.rectMode(CORNERS)
        self._image.ellipseMode(CORNERS)

        self._image.textFont(self.font)
        self._image.textAlign(LEFT, BOTTOM)
        self._image.textSize(20)
        self._image.fill(100)
        self._image.text("Window FPS : " + str(frameRate), 50, 50)

        super(Window, self).render(self._image)

        self._image.endDraw()

    def resize(self, x1, y1, x2, y2):
        super(Window, self).resize(x1, y1, x2, y2)
        self._image = createGraphics(int(self.get_width()), int(self.get_height()), P3D)
        self.update_buffer()
        return self

    def update(self, event):
        super(Window, self).update(event)
        self.update_buffer()

    def render(self):
        imageMode(CORNERS)
        image(self._image, self._pos_1.x, self._pos_1.y, self._pos_2.x, self._pos_2.y)

class ButtonBase(Widget):
    def __init__(self):
        super(ButtonBase, self).__init__()
        self._selected = False
        self._highlight = False

        self.set_press_callback(lambda: None)
        self.set_pressed_callback(lambda: None)
        self.set_released_callback(lambda: None)

    def is_selected(self): return self._selected
    def is_highlight(self): return self._highlight

    def set_press_callback(self, callback):
        self.press_callback = callback
        return self

    def set_pressed_callback(self, callback):
        self.pressed_callback = callback
        return self

    def set_released_callback(self, callback):
        self.released_callback = callback
        return self

    def update(self, event):
        p1 = self.parent.get_absolute_pos(self._pos_1)
        p2 = self.parent.get_absolute_pos(self._pos_2)

        prev_select = self._selected

        self._highlight = False
        self._selected = False
    
        if p1.x < event.mouse_pos().x < p2.x and p1.y < event.mouse_pos().y < p2.y:
            self._highlight = True
            self._selected = event.mouse_is_pressed()

        if self.is_selected():
            self.press_callback()
            if not prev_select:
                self.pressed_callback()
        elif prev_select:
            self.released_callback()

        return self

class Box(Widget):
    def __init__(self):
        super(Box, self).__init__()
        self.set_color()
        self.set_border_color()
        self.set_border_size()
        self.set_border_radius()

    def set_color(self, val = 95):
        self.color = val
        return self
    
    def set_border_color(self, val = 80):
        self.border_color = val
        return self

    def set_border_size(self, val = 1):
        self.border_size = val
        return self

    def set_border_radius(self, val = 1):
        self.border_radius = val
        return self

    def render(self, buffer):
        p1 = self.parent.get_absolute_pos(self._pos_1)
        p2 = self.parent.get_absolute_pos(self._pos_2)

        buffer.strokeWeight(self.border_size)
        buffer.stroke(self.border_color)
        buffer.fill(self.color)

        buffer.rect(p1.x, p1.y, p2.x, p2.y, self.border_radius)
        return self

class Text(Widget):
    class TextAlign(object):
        LEFT = 0
        CENTER = 1
        RIGHT = 2

    def __init__(self):
        super(Text, self).__init__()
        self.set_text()
        self.set_size()
        self.set_color()
        self.set_align()

    def set_text(self, val = ""):
        self.text = val
        return self

    def set_size(self, val = 50):
        self.size = val
        return self

    def set_color(self, val = 0):
        self.color = val
        return self

    def set_align(self, val = TextAlign.CENTER):
        self.align = val
        return self

    def render(self, buffer):
        p1 = self.parent.get_absolute_pos(self._pos_1)
        p2 = self.parent.get_absolute_pos(self._pos_2)

        if self.text != "":
            f_size = self.size

            if f_size == 0:
                f_size = min(2 * (p2.x - p1.x) / len(self.val), (p2.y - p1.y) / 2)

            if f_size != 0:
                buffer.textSize(f_size)
                buffer.fill(self.color)
                buffer.noStroke()

                if self.align == Text.TextAlign.CENTER:
                    buffer.textAlign(CENTER, CENTER)
                    buffer.text(self.text, (p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
                elif self.align == Text.TextAlign.LEFT:
                    buffer.textAlign(LEFT, CENTER)
                    buffer.text(self.text, p1.x, (p1.y + p2.y) / 2)
                elif self.align == Text.TextAlign.RIGHT:
                    buffer.textAlign(RIGHT, CENTER)
                    buffer.text(self.text, p2.x, (p1.y + p2.y) / 2)
        return self

class Image(Widget):
    def __init__(self):
        super(Image, self).__init__()
        self.image = None

    def set_image(self, image):
        self.image = image
        return self

    def render(self, buffer):
        p1 = self.get_absolute_pos(self._pos_1)
        p2 = self.get_absolute_pos(self._pos_2)

        buffer.fill(0)
        buffer.rect(p1.x, p1.y, p2.x, p2.y)

        if buffer != None and self.image != None:
            buffer.image(self.image, p1.x, p1.y, p2.x, p2.y)

class Label(Widget):
    def __init__(self):
        super(Label, self).__init__()
        self.caption = Text().set_parent(self)
        self.frame = Box().set_parent(self)

    def apply_fun(self, fun):
        super(Label, self).apply_fun(fun)
        self.caption.apply_fun(fun)
        self.frame.apply_fun(fun)

    def render(self, buffer):
        self.frame.render(buffer)
        self.caption.render(buffer)
        return self

class Button(ButtonBase):
    def __init__(self):
        super(Button, self).__init__()
        self.frame = Box().set_parent(self)
        self.caption = Text().set_parent(self)

    def apply_fun(self, fun):
        super(Button, self).apply_fun(fun)
        self.caption.apply_fun(fun)
        self.frame.apply_fun(fun)

    def render(self, buffer):
        self.frame.render(buffer)
        self.caption.render(buffer)
        return self
