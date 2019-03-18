import user_interface as UI

bgcol = 0

btncol = 20
btnfnt = 100
BTNcol = 40
BTNfnt = 20

lbcol = 10
lbfnt = 90

def set_style(elem):
    if isinstance(elem, UI.Button):
        elem.caption.set_color(btnfnt)
        elem.frame.set_color(btncol)
    else:
        elem.caption.set_color(lbfnt)
        elem.frame.set_color(lbcol)
        
    elem.frame.set_border_size(0)
    elem.frame.set_border_radius(10000)

def set_style_highlight(elem):
    set_style(elem)
    elem.caption.set_color(BTNfnt)
    elem.frame.set_color(BTNcol)

def set_callback(button, callback):
    def r(x):
        callback()
    
    def u(x):
        if button.is_highlighted() or button.is_selected():
            set_style_highlight(button)
        else:
            set_style(button)
    
    return button.set_update_callback(u).set_released_callback(r)

def create_button(x1 = 0, y1 = 0, x2 = 1, y2 = 1, text = "", callback = lambda: None):
    button = UI.Button().set_corners(x1, y1, x2, y2)

    set_style(button)
    button.caption.set_text(text)

    return set_callback(button, callback)

def create_label(x1, y1, x2, y2, text):
    label = UI.Label().set_corners(x1, y1, x2, y2)
    set_style(label)
    label.caption.set_text(text)

    return label

class UI_State(object):
    def __init__(self, parent):
        self.parent = parent
        self.parent.window.clear_widgets()
        self.parent.window.set_background(bgcol)
        self.update_func = lambda x: None

        self.left_frame = UI.Panel()
        self.center_frame = UI.Panel()
        self.right_frame = UI.Panel()

        self.parent.window.add_widget(self.center_frame).add_widget(self.left_frame).add_widget(self.right_frame)

    def update(self, event):
        r = self.parent.window.get_height()/self.parent.window.get_width()

        self.left_frame.set_corners(0, 0, r, 1)
        self.center_frame.set_corners((1-r)/2, 0, (1+r)/2, 1)
        self.right_frame.set_corners(1-r, 0, 1, 1)

        if event.get_event_time() > 20:
            event.poll()

            self.parent.window.update(event)
            self.update_func(event)
            self.parent.window.render()

    def add_widget(self, widget):
        self.parent.window.add_widget(widget)
