import user_interface as UI
import game_logic as PAC
import events as Events

keyboard = Events.KeyBoard_Event()
mouse = Events.Mouse_Event()

window_width = 1000
window_height = 1000

class UI_State(object):
    def __init__(self, parent_state):
        self.parent_state = parent_state
        self.parent_state.window.clear_widgets()
        self.parent_state.window.set_background(0)
        self.update_func = lambda: None

    def update(self, event):
        if event.get_event_time() > 1:
            event.poll()
            self.parent_state.window.update(event)
            self.update_func()
        self.parent_state.window.render()

    def add_widget(self, widget):
        self.parent_state.window.push_widget(widget)

    def add_button(self, x1, y1, x2, y2, text, callback):
        button = UI.Button().resize(x1, y1, x2, y2)
        button.caption.set_text(text)
        button.caption.set_color(100)

        button.frame.set_color(10)
        button.frame.set_border_size(2)
        button.frame.set_border_radius(10)

        def p():
            button.frame.set_color(20)

        def r():
            button.frame.set_color(10)
            callback()

        self.parent_state.window.push_widget(button.set_pressed_callback(p).set_released_callback(r))

class UI_MainMenu(UI_State):
    def __init__(self, parent_state):
        super(UI_MainMenu, self).__init__(parent_state)
        self.add_button(0.2, 0.50, 0.8, 0.58, "PLAY", self.parent_state.set_player)
        self.add_button(0.2, 0.60, 0.8, 0.68, "EDITOR", self.parent_state.set_editor)
        self.add_button(0.2, 0.70, 0.8, 0.78, "SETTINGS", self.parent_state.set_settings)
        self.add_button(0.2, 0.80, 0.8, 0.88, "QUIT", self.parent_state.set_quit)

class UI_Player(UI_State):
    def __init__(self, parent_state):
        super(UI_Player, self).__init__(parent_state)
        self.parent_state.load_game_state()

        self.maze_window = UI.Image().resize(0.05, 0.05, 0.95, 0.95)
        self.add_widget(self.maze_window)
        self.add_button(0, 0, 0.2, 0.1, "BACK", self.parent_state.set_main_menu)
        
        def _update():
            self.parent_state.update_game_state()
            self.maze_window.set_image(self.parent_state.get_game_window())
        self.update_func = _update
        
class UI_Settings(UI_State):
    def __init__(self, parent_state):
        super(UI_Settings, self).__init__(parent_state)
        self.add_button(0.2, 0.50, 0.8, 0.58, "KEY BINDINGS", lambda: None) #self.parent_state.set_keybindings)
        self.add_button(0.2, 0.60, 0.8, 0.68, "BACK", self.parent_state.set_main_menu)

class UI_Editor(UI_State):
    def __init__(self, parent_state):
        super(UI_Editor, self).__init__(parent_state)
        self.add_button(0.2, 0.80, 0.8, 0.88, "BACK", self.parent_state.set_main_menu)

class UserInterface(object):
    def load_game_state(self):
        self.game = PAC.Game()
        
    def update_game_state(self):
        self.game.update()
    
    def get_game_window(self):
        return self.game.get_frame_buffer()
    
    def change_state(self, create_state):
        self.previous_state = self.current_state
        self.current_state = create_state(self) 

    def set_undo_state(self):
        self.current_state = self.previous_state

    def set_quit(self):
        exit()

    def set_main_menu(self):
        self.change_state(UI_MainMenu)

    def set_player(self):
        self.change_state(UI_Player)

    def set_editor(self):
        self.change_state(UI_Editor)

    def set_settings(self):
        self.change_state(UI_Settings)

    def __init__(self):
        self.window = UI.Window().resize(0, 0, window_width, window_height)
        self.current_state = UI_MainMenu(self)

    def update(self, event):
        self.current_state.update(event)

class MainState(object):
    def __init__(self):
        self.stop_loop = False

        try:
            self.event = Events.Event(keyboard, mouse)
            self.user_interface = UserInterface()
        except Exception as ex:
            print("Initialization Error : " + str(ex))
            self.stop_loop = True
            
    def update(self):
        if not self.stop_loop:
            try:
                self.user_interface.update(self.event)
            except Exception as ex:
                print("Runtime Error : " + str(ex))
                self.stop_loop = True

def setup():
    global window_width
    global window_height
    global shader_1
    
    size(window_width, window_height, P3D)
    noSmooth()
    
    shader_1 = loadShader("blackwhite.glsl")

    hint(DISABLE_TEXTURE_MIPMAPS)
    g.textureSampling(3)

    global main_state
    main_state = MainState()

def draw():
    global main_state
    global shader_1

    shader(shader_1)

    main_state.update()

def keyPressed():
    keyboard.press()

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
