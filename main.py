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

class State(object):
    def __init__(self, parent_state):
        self.parent_state = parent_state

        self.parent_state.window.clear_elem()
        self.parent_state.window.push_elem(GUI.Box(0, 0, 1, 1, self.parent_state.back_theme))

    def change_state(self, state):
        self.parent_state.current_state = state(self.parent_state)

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

class State_MainMenu(State):
    def set_player(self):
        self.change_state(State_Player)

    def set_editor(self):
        self.change_state(State_Editor)

    def set_settings(self):
        self.change_state(State_Settings)

    def set_quit(self):
        self.parent_state.quit()

    def __init__(self, parent_state):
        super(State_MainMenu, self).__init__(parent_state)
        self.add_button(0.2, 0.50, 0.8, 0.58, "PLAY", self.set_player)
        self.add_button(0.2, 0.60, 0.8, 0.68, "EDITOR", self.set_editor)
        self.add_button(0.2, 0.70, 0.8, 0.78, "SETTINGS", self.set_settings)
        self.add_button(0.2, 0.80, 0.8, 0.88, "QUIT", self.set_quit)

class State_Player(State):
    def set_back(self):
        self.change_state(State_MainMenu)

    def __init__(self, parent_state):
        super(State_Player, self).__init__(parent_state)
        self.add_button(0, 0, 0.2, 0.1, "BACK", self.set_back)

class State_Settings(State):
    def set_keybindings(self):
        self.change_state(State_KeyBindings)

    def set_back(self):
        self.change_state(State_MainMenu)

    def __init__(self, parent_state):
        super(State_Settings, self).__init__(parent_state)
        self.add_button(0.2, 0.50, 0.8, 0.58, "KEY BINDINGS", self.set_keybindings)
        self.add_button(0.2, 0.60, 0.8, 0.68, "BACK", self.set_back)

class State_KeyBindings(State):
    def set_back(self):
        self.change_state(State_MainMenu)

    def __init__(self, parent_state):
        super(State_KeyBindings, self).__init__(parent_state)
        self.add_button(0.2, 0.10, 0.8, 0.18, "KEY UP    - ", lambda: None)
        self.add_button(0.2, 0.20, 0.8, 0.28, "KEY DOWN  - ", lambda: None)
        self.add_button(0.2, 0.30, 0.8, 0.38, "KEY LEFT  - ", lambda: None)
        self.add_button(0.2, 0.40, 0.8, 0.48, "KEY RIGHT - ", lambda: None)
        self.add_button(0.2, 0.50, 0.8, 0.58, "BACK", self.set_back)

class State_Editor(State):
    def set_main_menu(self):
        self.change_state(State_MainMenu)

    def __init__(self, parent_state):
        super(State_Editor, self).__init__(parent_state)
        self.add_button(0.2, 0.80, 0.8, 0.88, "BACK", self.set_main_menu)

class UI_Controller(object):
    def quit(self):
        exit()

    def __init__(self):
        self.back_theme = GUI.Theme(100, 95, 1, 20, 50)
        self.default_theme = GUI.Theme(95, 90, 1, 20, 50)
        self.highlight_theme = GUI.Theme(100, 95, 1, 20, 50)

        self.window = GUI.Window(0, 0, window_width, window_height)

        self.current_state = State_MainMenu(self)

    def update(self, event):
        self.current_state.update(event)

class GameState:
    def __init__(self):
        try:
            self.event = Events.Event(keyboard, mouse)
            self.main_menu = UI_Controller()
        except Exception as ex:
            print("Gamestate err : " + str(ex))

    def update(self):
        self.main_menu.update(self.event)

def setup():
    global window_width
    global window_height

    font = createFont("Fonts\RobotoMono-Thin", 100)
    textFont(font)
    size(window_width, window_height)

    try:
        global game_state
        game_state = GameState()

        colorMode(RGB, 100)
        rectMode(CENTER)    
    except Exception as ex:
        print("Setup Error: " + str(ex))

def draw():
    try:
        global game_state
        game_state.update()
    except Exception as ex:
        print("Runtime error: " + str(ex))

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