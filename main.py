import GUI
import Renderer
import Events
import Mover

keyboard = Events.KeyBoard_Event()
mouse = Events.Mouse_Event()

window_width = 1000
window_height = 1000

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


class GameState:
    class MainMenu:
        def __init__(self):
            self.back_theme = GUI.Theme(100, 95)
            self.default_theme = GUI.Theme(95, 90, 1)
            self.highlight_theme = GUI.Theme(100, 95, 1)

            self.win = GUI.Window(0, 0, window_width, window_height)
            self.win.push_elem(GUI.Box(-1, -1, 2, 2, self.back_theme))

            self.buttons = []
            self.textbox = []

            def add_button(x1, y1, x2, y2, txt):
                t = GUI.TextBox(x1, y1, x2, y2, txt, self.default_theme)
                self.textbox.append(t)

                def p_fun():
                    if t.get_theme() != self.default_theme:
                        t.set_theme(self.default_theme)
                    else:
                        t.set_theme(self.highlight_theme)

                self.buttons.append(GUI.Button(x1, y1, x2, y2, p_fun))

            add_button(0.2, 0.1, 0.8, 0.25, "1 PLAYER")
            add_button(0.2, 0.3, 0.8, 0.45, "EDITOR")
            add_button(0.2, 0.5, 0.8, 0.65, "SETTINGS")
            add_button(0.2, 0.7, 0.8, 0.85, "INFO")

            for i in self.buttons:
                self.win.push_elem(i)
            for i in self.textbox:
                self.win.push_elem(i)

        def cycle(self, event):
            if event.get_event_time() > 10:
                event.poll()
                self.win.update(event)
            self.win.render()

    def __init__(self):
        try:
            self.main_menu = GameState.MainMenu()

            self.maze_state = MazeState()

            self.event = Events.Event(keyboard, mouse)
            self.cursor = PVector(0, 0)
        except Exception as ex:
            print("Gamestate err : " + str(ex))

    def draw_main_menu(self):
        self.main_menu.cycle(self.event)

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

    def init(self):
        self.mode = self.draw_main_menu

    def update(self):
        self.mode()

def setup():
    global window_width
    global window_height

    font = createFont("Fonts\RobotoMono-Thin", 100)
    textFont(font)
    size(window_width, window_height)

    try:
        global game_state
        game_state = GameState()
        game_state.init()

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