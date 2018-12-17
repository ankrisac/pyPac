class Widget(object):
    def __init__(self):
        self.set_corners(0, 0, 1, 1)
        self.parent = None

    def apply_fun(self, fun):
        fun(self)
        return self

    def set_parent(self, parent):
        self.parent = parent
        return self

    def set_corners(self, x1, y1, x2, y2):
        self.pos_1 = PVector(x1, y1)
        self.pos_2 = PVector(x2, y2)
        return self

    def set_pos(self, x1, y1):
        w = self.pos_2.x - self.pos_1.x
        h = self.pos_2.y - self.pos_1.y

        self.set_corners(x1, y1, x1 + w, y1 + w)

    def resize(self, w, h):
        self.pos_2 = PVector(self.pos_1.x + w, self.pos_2.y + h)

    def get_width(self): 
        return self.pos_2.x - self.pos_1.x
    
    def get_height(self): 
        return self.pos_2.y - self.pos_1.y

    def get_absolute_pos(self, pos):
        t_pos = self.pos_1 + PVector(self.get_width() * pos.x, self.get_height() * pos.y)
        
        if self.parent != None:
            return self.parent.get_absolute_pos(t_pos)
        else:
            return t_pos

    def get_absolute_dimensions(self):
        return self.get_absolute_pos(self.pos_2) - self.get_absolute_pos(self.pos_1)

    def get_absolute_width(self):
        return self.get_absolute_dimensions().x

    def get_absolute_height(self):
        return self.get_absolute_dimensions().y

    def update(self, event): 
        return self
    
    def render(self, buffer): 
        return self

class NoneWidget(Widget):
    pass

class Panel(Widget):
    def __init__(self):
        self._child_widgets = []
        super(Panel, self).__init__()

    def apply_fun(self, fun):
        fun(self)

        for i in self._child_widgets:
            i.apply_fun(fun)

    def add_widget(self, elem):
        self._child_widgets.append(elem.set_parent(self))
        return self
    
    def add_widget_list(self, lst):
        for i in lst:
            self._child_widgets.append(i.set_parent(self))
        return self

    def pop_widget(self):
        return self._child_widgets.pop()

    def clear_widgets(self):
        self._child_widgets = []
        return self

    def set_widget(self, i, elem):
        self._child_widgets[i] = elem
        return self

    def get_widget(self, i): 
        return self._child_widgets[i]

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
        super(Window, self).__init__()

        self.font = createFont("Courier New", 100)
        self.set_font_size()
        self.set_background(100)
        self.set_shader(None)
        self.resize_buffer()
 
    def set_font_size(self, font_size = 20):
        self.font_size = font_size
        return self

    def set_background(self, col):
        self.background = col
        return self

    def set_shader(self, shader):
        self._shader = shader
        return self

    def update_buffer(self):
        if self._buffer != None:
            self._buffer.noSmooth()
            self._buffer.beginDraw()
    
            self._buffer.colorMode(RGB, 100)
            self._buffer.background(self.background)
    
            self._buffer.imageMode(CORNERS)
            self._buffer.rectMode(CORNERS)
            self._buffer.ellipseMode(CORNERS)
    
            self._buffer.textFont(self.font)
            self._buffer.textAlign(LEFT, BOTTOM)
            self._buffer.textSize(self.font_size)
            self._buffer.fill(100)
            self._buffer.text("Window FPS : " + str(frameRate), 50, 50)
    
            super(Window, self).render(self._buffer)
    
            self._buffer.endDraw()
        return self

    def resize_buffer(self, w = 1, h = 1):
        if w > 0 and h > 0:
            self._buffer = createGraphics(int(w), int(h), P3D)
            self.update_buffer()
        return self

    def update(self, event):
        super(Window, self).update(event)
        self.update_buffer()
        return self

    def render(self):
        if self._shader != None:
            shader(self._shader)

        imageMode(CORNERS)
        image(self._buffer, self.pos_1.x, self.pos_1.y, self.pos_2.x, self.pos_2.y)

        resetShader()
        return self

class ButtonBase(Widget):
    def __init__(self):
        super(ButtonBase, self).__init__()
        self._selected = False
        self._highlight = False

        self.set_update_callback(lambda x: None)
        self.set_pressed_callback(lambda x: None)
        self.set_released_callback(lambda x: None)

    def is_selected(self): 
        return self._selected

    def is_highlighted(self): 
        return self._highlight

    def set_update_callback(self, callback):
        self.update_callback = callback
        return self

    def set_pressed_callback(self, callback):
        self.pressed_callback = callback
        return self

    def set_released_callback(self, callback):
        self.released_callback = callback
        return self

    def update(self, event):
        p1 = self.parent.get_absolute_pos(self.pos_1)
        p2 = self.parent.get_absolute_pos(self.pos_2)

        prev_select = self._selected

        self._highlight = False
        self._selected = False
    
        if p1.x < event.mouse_pos().x < p2.x and p1.y < event.mouse_pos().y < p2.y:
            self._selected = event.mouse_is_pressed()

            if not self._selected:
                self._highlight = True

        if self.is_selected():
            if not prev_select:
                self.pressed_callback(event)
        elif prev_select:
            self.released_callback(event)
        
        self.update_callback(event)

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
        p1 = self.parent.get_absolute_pos(self.pos_1)
        p2 = self.parent.get_absolute_pos(self.pos_2)

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

    def set_size(self, val = None):
        self.size = val
        return self

    def set_color(self, val = 0):
        self.color = val
        return self

    def set_align(self, val = TextAlign.CENTER):
        self.align = val
        return self

    def render(self, buffer):
        p1 = self.parent.get_absolute_pos(self.pos_1)
        p2 = self.parent.get_absolute_pos(self.pos_2)

        if self.text != "":
            f_size = self.size

            if f_size == 0 or f_size == None:
                f_size = min(2 * (p2.x - p1.x) / len(self.text), (p2.y - p1.y) / 2)

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

class FrameBuffer(Widget):
    def __init__(self):
        super(FrameBuffer, self).__init__()
        self.set_buffer()
        self.set_buffer_corners()
        self.set_shader()

    def set_buffer_corners(self, x1 = 0, y1 = 0, x2 = 1, y2 = 1):
        self.buffer_pos_1 = PVector(x1, y1)
        self.buffer_pos_2 = PVector(x2, y2)

    def set_shader(self, shader = None):
        self.shader = shader

    def set_buffer(self, image = None):
        self.image = image
        return self

    def render(self, buffer):
        p1 = self.get_absolute_pos(self.pos_1)
        p2 = self.get_absolute_pos(self.pos_2)

        buffer.fill(0)
        buffer.rect(p1.x, p1.y, p2.x, p2.y)

        if self.shader != None:
            buffer.shader(self.shader)

        if buffer != None and self.image != None:
            buffer.pushMatrix()
            buffer.translate(p1.x, p1.y)
            buffer.scale(p2.x - p1.x, p2.y - p1.y)
            buffer.image(self.image, self.buffer_pos_1.x, self.buffer_pos_1.y, self.buffer_pos_2.x, self.buffer_pos_2.y)
            buffer.popMatrix()

        buffer.resetShader()

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
