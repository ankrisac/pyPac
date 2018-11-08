class Elem(object):
    def resize(self, x1, y1, x2, y2):
        self._pos_1 = PVector(x1, y1)
        self._pos_2 = PVector(x2, y2)

    def __init__(self, x1 = 0, y1 = 0, x2 = 1, y2 = 1):
        self.resize(x1, y1, x2, y2)
        self.parent = None

    def get_width(self):
        return self._pos_2.x - self._pos_1.x
    
    def get_height(self):
        return self._pos_2.y - self._pos_1.y

    def _scale_pos(self, pos):
        t_pos = self._pos_1 + PVector(self.get_width() * pos.x, self.get_height() * pos.y)

        if self.parent != None:
            return self.parent._scale_pos(t_pos)
        return t_pos

    def update(self, event):
        pass
        
    def render(self, buffer):
        pass

class Frame(Elem):
    def push_elem(self, elem):
        self._elems.append(elem)
        self._elems[-1].parent = self

    def __init__(self, x1 = 0, y1 = 0, x2 = 1, y2 = 1, lst = []):
        super(Frame, self).__init__(x1, y1, x2, y2)

        self._elems = []
        for i in lst:
            self.push_elem(i)

    def get_elem(self, i):
        return self._elems[i]

    def clear_elem(self):
        self._elems = []

    def pop_elem(self):
        self._elems.pop()

    def set_elem(self, i, elem):
        self._elems[i] = elem

    def update(self, event):
        for i in self._elems:
            i.update(event)
        
    def render(self, buffer):
        for i in self._elems:
            i.render(buffer)

class Window(Frame):
    def __init__(self, x1 = 0, y1 = 0, x2 = 1, y2 = 1):
        super(Window, self).__init__(x1, y1, x2, y2)
        self._image = createGraphics(int(self.get_width()), int(self.get_height()))

    def render(self):
        self._image.beginDraw()
        self._image.colorMode(RGB, 100)
        self._image.background(0)

        super(Window, self).render(self._image)

        self._image.endDraw()

        image(self._image, self._pos_1.x, self._pos_1.y, self.get_width(), self.get_height())

class Button(Elem):
    def __init__(self, x1 = 0, y1 = 0, x2 = 1, y2 = 1, pressed_callback = lambda: None, released_callback = lambda: None):
        super(Button, self).__init__(x1, y1, x2, y2)
        self._selected = False
        self._highlight = False
        self.pressed_callback = pressed_callback
        self.released_callback = released_callback

    def is_selected(self):
        return self._selected

    def is_highlighted(self):
        return self._highlight

    def update(self, event):
        p1 = self.parent._scale_pos(self._pos_1)
        p2 = self.parent._scale_pos(self._pos_2)

        prev_select = self._selected

        self._highlight = False
        self._selected = False
    
        if p1.x < event.mouse_pos().x < p2.x:
            if p1.y < event.mouse_pos().y < p2.y:
                self._highlight = True
                self._selected = event.mouse_is_pressed()

        if not prev_select and self.is_selected():
            self.pressed_callback()

        if prev_select and not self.is_selected():
            self.released_callback()

class Theme(object):
    class TextMode:
        CENTER = 0
        LEFT = 1
        RIGHT = 2

    def __init__(self, color = 100, border_color = 90, border_size = 10, font_color = 10, font_size = 0):
        self.color = color
        self.border_color = border_color
        self.border_size = border_size

        self.font_color = font_color
        self.font_size = font_size
        self.text_mode = Theme.TextMode.CENTER

class DisplayElem(Elem):
    def __init__(self, x1 = 0, y1 = 0, x2 = 1, y2 = 1, theme = Theme()):
        super(DisplayElem, self).__init__(x1, y1, x2, y2)
        self._theme = theme

    def set_theme(self, theme):
        self._theme = theme

    def get_theme(self):
        return self._theme

class Box(DisplayElem):
    def __init__(self, x1 = 0, y1 = 0, x2 = 1, y2 = 1, theme = Theme()):
        super(Box, self).__init__(x1, y1, x2, y2, theme)

    def render(self, buffer):
        p1 = self.parent._scale_pos(self._pos_1)
        p2 = self.parent._scale_pos(self._pos_2)

        buffer.strokeWeight(self.get_theme().border_size)
        buffer.stroke(self.get_theme().border_color)
        buffer.fill(self.get_theme().color)

        buffer.rectMode(CORNERS)
        buffer.rect(p1.x, p1.y, p2.x, p2.y)

class Text(DisplayElem):
    def __init__(self, x1 = 0, y1 = 0, x2 = 1, y2 = 1, text = "", theme = Theme()):
        super(Text, self).__init__(x1, y1, x2, y2, theme)
        self._text = text

    def get_text(self):
        return self._text
        
    def set_text(self, text):
        self._text = text

    def render(self, buffer):
        p1 = self.parent._scale_pos(self._pos_1)
        p2 = self.parent._scale_pos(self._pos_2)

        if self._text != "":
            f_size = self.get_theme().font_size

            if self.get_theme().font_size == 0:
                f_size = min(2 * (p2.x - p1.x) / len(self._text), (p2.y - p1.y) / 2)

            if f_size != 0:
                buffer.textSize(f_size)
                buffer.fill(self.get_theme().font_color)
                buffer.noStroke()

                if self.get_theme().text_mode == Theme.TextMode.CENTER:
                    buffer.textAlign(CENTER, CENTER)
                    buffer.text(self._text, (p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
                elif self.get_theme().text_mode == Theme.TextMode.LEFT:
                    buffer.textAlign(LEFT, CENTER)
                    buffer.text(self._text, p1.x, (p1.y + p2.y) / 2)
                elif self.get_theme().text_mode == Theme.TextMode.RIGHT:
                    buffer.textAlign(RIGHT, CENTER)
                    buffer.text(self._text, p2.x, (p1.y + p2.y) / 2)

class TextBox(DisplayElem):
    def __init__(self, x1 = 0, y1 = 0, x2 = 1, y2 = 1, text = "", theme = Theme()):
        super(TextBox, self).__init__(x1, y1, x2, y2, theme)
        self._text = Text(0, 0, 1, 1, text, theme)
        self._box = Box(0, 0, 1, 1, theme)

        self._text.parent = self
        self._box.parent = self

    def get_text(self):
        return self._text.get_text()
        
    def set_text(self, text):
        self._text.set_text(text)

    def set_theme(self, theme):
        super(TextBox, self).set_theme(theme)
        self._text.set_theme(theme)
        self._box.set_theme(theme)

    def render(self, buffer):
        self._box.render(buffer)
        self._text.render(buffer)
