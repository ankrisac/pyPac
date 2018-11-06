import user_interface as GUI
import maze_renderer as Renderer
import events as Events
import maze_mover as Mover

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

class MainMenu(object):
    def __init__(self, parent):
        def _add_button(x1, y1, x2, y2, txt, callback):
            textbox = GUI.TextBox(x1, y1, x2, y2, txt, self.default_theme)

            def p_fun():
                textbox.set_theme(self.highlight_theme)
                callback()

            def r_fun():
                textbox.set_theme(self.default_theme)

            self.window_mainmenu.push_elem(textbox)
            self.window_mainmenu.push_elem(GUI.Button(x1, y1, x2, y2, p_fun, r_fun))

        self.back_theme = GUI.Theme(100, 95, 1, 20, 50)
        self.default_theme = GUI.Theme(95, 90, 1, 20, 50)
        self.highlight_theme = GUI.Theme(100, 95, 1, 20, 50)

        self.window_mainmenu = GUI.Window(0, 0, window_width, window_height)
        self.window_mainmenu.push_elem(GUI.Box(-1, -1, 2, 2, self.back_theme))

        x = 0.5
        y = 0.5

        w = 0.6
        h = 0.1
        
        dy = 0.025

        button_lst = [("PLAY", lambda: None),
                      ("EDITOR", lambda: None),
                      ("SETTINGS", lambda: None),
                      ("QUIT", lambda: None),]

        for i in button_lst:
            _add_button(x - 0.5 * w, y, x + 0.5 * w, y + h, i[0], i[1])
            y += h + dy

        self.win = self.window_mainmenu

    def update(self, event):
        if event.get_event_time() > 10:
            event.poll()
            self.win.update(event)
        self.win.render()

class GameState:
    def __init__(self):
        try:
            self.main_menu = MainMenu(self)
            self.update_func = self.main_menu.update

            self.maze_state = None

            self.event = Events.Event(keyboard, mouse)
            self.cursor = PVector(0, 0)
        except Exception as ex:
            print("Gamestate err : " + str(ex))

    def single_player(self):
        self.maze_state.render()

    def maze_editor(self):
        background(50)

        if self.event.get_event_time() > 100:
            self.event.poll()

            self.escape_to_menu()

            t_vec = self.cursor.copy()
            if self.event.key_is_pressed(Event.KEY_UP):
                t_vec += PVector(0, -1)
            if self.event.key_is_pressed(Event.KEY_DOWN):
                t_vec += PVector(0, +1)
            if self.event.key_is_pressed(Event.KEY_LEFT):
                t_vec += PVector(-1, 0)
            if self.event.key_is_pressed(Event.KEY_RIGHT):
                t_vec += PVector(+1, 0)

            if self.maze.is_valid_cell(t_vec.x, t_vec.y):
                self.cursor = t_vec
            for x in range(Cell.CELL_BEGIN, Cell.CELL_END + 1):
                if self.event.key_is_pressed(str(x)):
                    self.maze.update_cell(int(self.cursor.x), int(self.cursor.y), x)

        def _cell_func(R):
            strokeWeight(R/10)
            stroke(100, 100)
            fill(100, 25)
            rect(0, 0, R, R)

        self.maze.draw_maze()
        self.maze.render_cell(self.cursor.x, self.cursor.y, _cell_func)

    def update(self):
        self.update_func(self.event)

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
