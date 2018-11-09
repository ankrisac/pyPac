import user_interface as GUI
import maze_renderer as Renderer
import events as Events
import maze_entity as Mover

keyboard = Events.KeyBoard_Event()
mouse = Events.Mouse_Event()

window_width = 1000
window_height = 1000

"""
class MazeState:
    def __init__(self):
        self._event = Events.Event(keyboard, mouse)

        try:
            self._maze = Renderer.MazeRenderer()

            E = Renderer.Cell.FOOD_PELLET_SMALL
            R = Renderer.Cell.WALL_ROUND
            S = Renderer.Cell.WALL_SQUARE
            P = Renderer.Cell.FOOD_PELLET_LARGE

            arr =  [[S,S,S,S,S,S,S,S,S,S,S],
                    [S,E,E,E,E,E,E,E,E,E,S],
                    [S,E,P,E,E,E,E,E,E,E,S],
                    [S,E,E,E,P,P,E,E,E,E,S],
                    [S,E,E,E,E,E,E,E,E,E,S],
                    [S,E,E,R,E,E,E,S,E,E,S],
                    [S,E,E,E,E,E,E,S,E,E,S],
                    [S,E,E,E,E,E,E,S,E,E,S],
                    [S,E,E,S,S,S,S,S,E,E,S],
                    [S,E,E,E,E,E,E,E,E,E,S],
                    [S,S,S,S,S,S,S,S,S,S,S]]

            self._maze.resize(int(0.1 * window_width), int(0.1 * window_height), int(0.8 * window_width), int(0.8 * window_height))
            self._maze.update_buffer(arr)

            self._players = [Mover.Player(1, 1)]
            self._ghosts = [Mover.Ghost(1, 1), Mover.Ghost(1, 1)]
            
            self._score = 0
            self._no_clip = False

        except Exception as ex:
            print("Maze loading error: " + str(ex))

    def render(self):
        background(0)

        self._maze.render()

        if self._event.get_event_time() > 10:
            self._event.poll()

            for i in self._players:
                i.update(self)
            for j in self._ghosts:
                j.update(self)

        for i in self._players:
            i.render(self)
        for j in self._ghosts:
            j.render(self)
"""

class UI_State(object):
    def __init__(self, parent_state):
        self.parent_state = parent_state

        self.parent_state.window.clear_elem()
        self.parent_state.window.push_elem(GUI.Box(0, 0, 1, 1, self.parent_state.back_theme))

    def update(self, event):
        if event.get_event_time() > 10:
            event.poll()
            self.parent_state.window.update(event)

        self.parent_state.window.render()

    def add_button(self, x1, y1, x2, y2, txt, callback):
        textbox = GUI.TextBox(x1, y1, x2, y2, txt, self.parent_state.default_theme)

        def p_fun():
            textbox.set_theme(self.parent_state.highlight_theme)

        def r_fun():
            textbox.set_theme(self.parent_state.default_theme)
            callback()

        self.parent_state.window.push_elem(textbox)
        self.parent_state.window.push_elem(GUI.Button(x1, y1, x2, y2, p_fun, r_fun))

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
        self.add_button(0, 0, 0.2, 0.1, "BACK", self.parent_state.set_main_menu)

class UI_Settings(UI_State):
    class KeyBindings(UI_State):
        def add_button(self, x1, y1, x2, y2, txt, text_mode, callback):
            self.default_theme = self.parent_state.default_theme
            self.highlight_theme = self.parent_state.highlight_theme

            self.default_theme.text_mode = text_mode
            self.highlight_theme.text_mode = text_mode

            textbox = GUI.TextBox(x1, y1, x2, y2, txt, self.default_theme)

            def p_fun():
                textbox.set_theme(self.highlight_theme)

            def r_fun():
                textbox.set_theme(self.default_theme)
                callback()

            self.parent_state.window.push_elem(textbox)
            self.parent_state.window.push_elem(GUI.Button(x1, y1, x2, y2, p_fun, r_fun))

        def __init__(self, parent_state):
            super(UI_Settings.KeyBindings, self).__init__(parent_state)
            self.add_button(0.2, 0.10, 0.8, 0.18, "KEY UP    - ", GUI.Theme.TextMode.LEFT, lambda: None)
            self.add_button(0.2, 0.20, 0.8, 0.28, "KEY DOWN  - ", GUI.Theme.TextMode.LEFT, lambda: None)
            self.add_button(0.2, 0.30, 0.8, 0.38, "KEY LEFT  - ", GUI.Theme.TextMode.LEFT, lambda: None)
            self.add_button(0.2, 0.40, 0.8, 0.48, "KEY RIGHT - ", GUI.Theme.TextMode.LEFT, lambda: None)
            self.add_button(0.2, 0.50, 0.8, 0.58, "BACK", GUI.Theme.TextMode.CENTER, self.parent_state.set_settings)

    def __init__(self, parent_state):
        super(UI_Settings, self).__init__(parent_state)
        self.add_button(0.2, 0.50, 0.8, 0.58, "KEY BINDINGS", self.parent_state.set_keybindings)
        self.add_button(0.2, 0.60, 0.8, 0.68, "BACK", self.parent_state.set_main_menu)

class UI_Editor(UI_State):
    def __init__(self, parent_state):
        super(UI_Editor, self).__init__(parent_state)
        self.add_button(0.2, 0.80, 0.8, 0.88, "BACK", self.parent_state.set_main_menu)

class UserInterface(object):
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

    def set_keybindings(self):
        self.change_state(UI_Settings.KeyBindings)

    def set_key(self, key_index, key_value):
        pass

    def __init__(self):
        self.back_theme = GUI.Theme(100, 95, 1, 20, 50)
        self.default_theme = GUI.Theme(95, 90, 1, 20, 50)
        self.highlight_theme = GUI.Theme(100, 95, 1, 20, 50)

        self.window = GUI.Window(0, 0, window_width, window_height)

        self.current_state = UI_MainMenu(self)

    def update(self, event):
        self.current_state.update(event)

class GameState(object):
    class KeyBindings(object):
        class KeyIndex(Enum):
            BEGIN = 0
        
            UP_1 = 1
            DOWN_1 = 2
            LEFT_1 = 3
            RIGHT_1 = 4

            UP_2 = 5
            DOWN_2 = 6
            LEFT_2 = 7
            RIGHT_2 = 8

            END = 9

    def set_keybinding(self, key, new_key):
        self.keybindings[key] = new_key

    def __init__(self):
        self.keybindings = [" " for i in range(GameState.KeyIndex.BEGIN, GameState.KeyIndex.END)]

        self.keybindings[GameState.KeyIndex.UP_1]    = "w"
        self.keybindings[GameState.KeyIndex.DOWN_1]  = "s"
        self.keybindings[GameState.KeyIndex.LEFT_1]  = "a"
        self.keybindings[GameState.KeyIndex.RIGHT_1] = "d"

        self.keybindings[GameState.KeyIndex.UP_1]    = Events.SPECIAL.KEY_UP
        self.keybindings[GameState.KeyIndex.DOWN_1]  = Events.SPECIAL.KEY_DOWN
        self.keybindings[GameState.KeyIndex.LEFT_1]  = Events.SPECIAL.KEY_LEFT
        self.keybindings[GameState.KeyIndex.RIGHT_1] = Events.SPECIAL.KEY_RIGHT

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

    font = createFont("Consolas", 100)
    textFont(font)
    size(window_width, window_height)

    global main_state
    main_state = MainState()

    colorMode(RGB, 100)
    rectMode(CENTER)    

def draw():
    global main_state
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