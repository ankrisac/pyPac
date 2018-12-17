add_library('minim')

import user_interface as UI
import game_logic as PAC
import events as Events
import os
import copy

keyboard = Events.KeyBoard_Event()
mouse = Events.Mouse_Event()

def set_style(elem):
    elem.caption.set_color(100)
    elem.frame.set_color(10)
    elem.frame.set_border_size(0)
    elem.frame.set_border_radius(0)

def set_style_highlight(elem):
    set_style(elem)
    elem.frame.set_color(20)
    elem.caption.set_color(90)

def set_callback(button, callback):
    def p(x):
        set_style_highlight(button)

    def r(x):
        set_style(button)
        callback()
    
    button.set_pressed_callback(p).set_released_callback(r)
    return button

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
        self.parent.window.set_background(0)
        self.update_func = lambda x: None

        self.left_frame = UI.Panel()
        self.center_frame = UI.Panel()
        self.right_frame = UI.Panel()

        self.parent.window.add_widget(self.left_frame).add_widget(self.center_frame).add_widget(self.right_frame)

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

class UI_MainMenu(UI_State):
    def __init__(self, parent):
        super(UI_MainMenu, self).__init__(parent)
        logo = create_label(0.2, 0.1, 0.8, 0.4, "")
        logo.frame = UI.NoneWidget()

        self.center_frame.add_widget(logo)

        for i in range(0, 4):
            self.center_frame.add_widget(create_button(0.2, 0.5 + 0.1 * i, 0.8, 0.58 + 0.1 * i, 
                                        ["Play", "Highscores", "Options", "Quit"][i],
                                        self.parent.create_state_changer([UI_Player, UI_Highscores, UI_Options, UI_Exit][i])))

        credit = create_label(0.5, 0.9, 1, 0.95, "Created By Sigmaphi")
        credit.frame = UI.NoneWidget()

        self.right_frame.add_widget(credit)

        def fn_update(event):
            if random(0, 10) < 2:
                l0 = 0
                l1 = 255
                txt = ""
                for i in "Arcade":
                    if random(0, 10) < 2:
                        txt += chr(int(random(l0, l1)))
                    else:
                        txt += i

                logo.caption.set_text(txt)

        self.update_func = fn_update

class UI_Player(UI_State):
    def __init__(self, parent):
        super(UI_Player, self).__init__(parent)
        game = PAC.PacMan(self.parent.minim)

        game_window = UI.FrameBuffer().set_corners(0.05, 0.05, 0.95, 0.95)
        game_window.set_shader(self.parent.shader_manager.get_game_shader())

        def quit_game():
            game.quit_game()
            self.parent.change_state(UI_MainMenu)

        back_button = create_button(0, 0, 0.2, 0.1, "BACK", quit_game)
        
        self.center_frame.add_widget(game_window)
        
        def _update(event):
            game.update(event)
            game_window.set_buffer(game.get_frame_buffer())

        self.update_func = _update
        self.left_frame.add_widget(back_button)

class Highscores(object):
    def __init__(self):
        pass

    def get_scores(self):
        return [" - : 0" for x in range(0, 6)]

class UI_Highscores(UI_State):
    def __init__(self, parent):
        super(UI_Highscores, self).__init__(parent)
        scores = Highscores().get_scores()

        padding = 0.02
        dy = 0.1
        y = 0.1
        for i in scores:
            self.center_frame.add_widget(create_label(0.2, y, 0.8, y + dy, i))
            y += dy + padding

        self.center_frame.add_widget(create_button(0.2, y, 0.8, y + dy, "Main Menu", self.parent.create_state_changer(UI_MainMenu)))

class UI_Options(UI_State):
    def __init__(self, parent):
        super(UI_Options, self).__init__(parent)
        
        ui_shader_button   = create_button(0.1, 0.3, 0.9, 0.38)
        game_shader_button = create_button(0.1, 0.4, 0.9, 0.48)

        def set_ui_caption():
            ui_shader_button.caption.set_text(self.parent.shader_manager.get_ui_shader_name())
        
        def set_game_caption():
            game_shader_button.caption.set_text(self.parent.shader_manager.get_game_shader_name())
        
        def change_ui_shader():
            self.parent.shader_manager.next_ui_shader()
            set_ui_caption()
            
        def change_game_shader():
            self.parent.shader_manager.next_game_shader()
            set_game_caption()

        set_ui_caption()
        set_game_caption()
        set_callback(ui_shader_button, change_ui_shader)
        set_callback(game_shader_button, change_game_shader)

        back_button = create_button(0.1, 0.5, 0.9, 0.58, "Back", self.parent.create_state_changer(UI_MainMenu))

        self.center_frame.add_widget_list([ui_shader_button, game_shader_button, back_button])

class UI_Exit(UI_State):
    def __init__(self, parent):
        super(UI_Exit, self).__init__(parent)
        self.center_frame.add_widget(create_label(0.2, 0.5, 0.8, 0.58, "Are you sure you want to quit ?").caption.set_size(40))
        self.center_frame.add_widget(create_button(0.2, 0.6, 0.4, 0.68, "Quit", exit))
        self.center_frame.add_widget(create_button(0.45, 0.6, 0.8, 0.68, "Cancel", self.parent.create_state_changer(UI_MainMenu)))

class ShaderManager(object):
    def __init__(self):
        self.load_shaders()
        self.current_ui_shader = 0
        self.current_game_shader = 0 

    def load_shaders(self):
        _path = sketchPath()
        
        def get_shaders_dir(path):
            shaders_path = filter(lambda x: os.path.isfile(os.path.join(path, x)), os.listdir(path))
            shaders_abs_path = map(lambda x: os.path.join(path, x), shaders_path)
            return shaders_abs_path

        def map_shader(name):
            return lambda i: (loadShader(i), name + " - " + os.path.splitext(os.path.basename(i))[0])

        self.ui_shaders = map(map_shader("UI Shader"), get_shaders_dir(os.path.join(_path, "shaders", "ui")) + get_shaders_dir(os.path.join(_path, "shaders")))
        self.game_shaders = map(map_shader("Game Shader"), get_shaders_dir(os.path.join(_path, "shaders", "game")) + get_shaders_dir(os.path.join(_path, "shaders")))
        
        return self
    
    def next_ui_shader(self):
        self.current_ui_shader += 1
        if self.current_ui_shader >= len(self.ui_shaders):
            self.current_ui_shader = 0
        return self

    def next_game_shader(self):
        self.current_game_shader += 1
        if self.current_game_shader >= len(self.game_shaders):
            self.current_game_shader = 0
        return self

    def get_ui_shader(self):
        (_shader, _) = self.ui_shaders[self.current_ui_shader]
        return _shader

    def get_ui_shader_name(self):
        (_, name) = self.ui_shaders[self.current_ui_shader]
        return name

    def get_game_shader(self):
        (_shader, _) = self.game_shaders[self.current_game_shader]
        return _shader

    def get_game_shader_name(self):
        (_, name) = self.game_shaders[self.current_game_shader]
        return name

class Arcade(object):
    def change_state(self, state_constructor):
        self.previous_state = self.current_state
        self.current_state = state_constructor(self)

    def create_state_changer(self, state_constructor):
        def change_state():
            self.change_state(state_constructor)
        
        return change_state

    def set_undo_state(self):
        self.current_state = self.previous_state

    def __init__(self):
        self.shader_manager = ShaderManager()
        self.game_shader = self.shader_manager.get_game_shader()

        self.window = UI.Window().set_shader(self.shader_manager.get_ui_shader())
        self.event = Events.Event(keyboard, mouse)
        self.current_state = UI_MainMenu(self)
        self.stop_loop = False

        self.minim = Minim(this)
        self.input = self.minim.getLineIn()

    def update(self):
        if not self.stop_loop:
            try:
                self.window.set_shader(self.shader_manager.get_ui_shader())
                self.current_state.update(self.event)
            except Exception as ex:
                print("Runtime Error : " + repr(ex))
                self.stop_loop = True

    def resize(self, w, h):
        self.window.set_corners(0, 0, w, h)
        self.window.resize_buffer(w, h)

def setup():
    global window_width
    global window_height

    size(800, 800, P3D)
    window_width = width
    window_height = height

    noSmooth()

    hint(DISABLE_TEXTURE_MIPMAPS)
    g.textureSampling(3)

    global arcade_state
    arcade_state = Arcade()
    arcade_state.resize(window_width, window_height)

def draw():
    global arcade_state
    global window_width
    global window_height

    if window_width != width or window_height != height:
        window_width = width
        window_height = height
        arcade_state.resize(window_width, window_height)

    arcade_state.update()

def keyPressed():
    keyboard.press()
    if this.key == ESC:
        this.key = " "

def keyReleased():
    keyboard.release()

def mousePressed():
    mouse.press()

def mouseReleased():
    mouse.release()

def mouseMoved():
    mouse.release()
    mouse.move()

def mouseDragged():
    mouse.press()
    mouse.move()
