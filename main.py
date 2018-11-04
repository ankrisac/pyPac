import GUI

def r_vel():
    if random(0, 1) <= 0.5:
        if random(0, 1) <= 0.5:
            return PVector(1, 0)
        else:
            return PVector(0, 1)
    else:
        if random(0, 1) <= 0.5:
            return PVector(-1, 0)
        else:
            return PVector(0, -1)

def joinfunc(func_lst):
    def product(buffer, R):
        for func in func_lst:
            func(buffer, R)
    return product
def rotatefunc(func, angle):
    def _rotated_func(buffer, R):
        buffer.pushMatrix()
        buffer.rotate(angle)
        func(buffer, R)
        buffer.popMatrix()
    return _rotated_func

def cell_empty(buffer, R): 
    buffer.fill(0)
    buffer.stroke(10)
    buffer.rect(0, 0, 0.5*R, 0.5*R)
def cell_box(buffer, R):
    buffer.stroke(100)
    buffer.rect(0, 0, 0.5*R, 0.5*R)

def cell_food_small(buffer, R):
    buffer.fill(100, 100, 0)
    buffer.noStroke()
    buffer.ellipse(0, 0, 0.125*R, 0.125*R)

def cell_food_large(buffer, R):
    buffer.fill(100, 100, 0)
    buffer.noStroke()
    buffer.ellipse(0, 0, 0.25*R, 0.25*R)

def left_wall(buffer, R):
    buffer.stroke(100)
    buffer.line(-0.25*R, 0, -0.25*R, 0.5*R)
def right_wall(buffer, R):
    buffer.stroke(100)
    buffer.line(0.25*R, 0, 0.25*R, 0.5*R)
    
def inner_square_corner(buffer, R):
    buffer.stroke(100)
    buffer.line(0.25*R, 0.25*R, 0.5*R, 0.25*R)
    buffer.line(0.25*R, 0.25*R, 0.25*R, 0.5*R)
def outer_square_corner(buffer, R):
    buffer.stroke(100)
    buffer.line(-0.25*R, 0.25*R, 0.25*R, 0.25*R) 
    buffer.line(0.25*R, -0.25*R, 0.25*R, 0.25*R)
    
def inner_round_corner(buffer, R):
    buffer.stroke(100)
    buffer.arc(0.5*R, 0.5*R, 0.25*R, 0.25*R, TAU*0.5, TAU*0.75)
def outer_round_corner(buffer, R):
    buffer.stroke(100)
    buffer.arc(0, 0, 0.25*R, 0.25*R, 0, TAU*0.25)

class Cell:
    CELL_BEGIN = 0
    NONE  = 0
    EMPTY = 1
    
    FOOD_BEGIN        = EMPTY + 1
    FOOD_PELLET_SMALL = FOOD_BEGIN
    FOOD_PELLET_LARGE = FOOD_BEGIN + 1
    FOOD_END          = FOOD_BEGIN + 1

    WALL_BEGIN  = FOOD_END + 1
    WALL_ROUND  = WALL_BEGIN
    WALL_SQUARE = WALL_BEGIN + 1
    WALL_END    = WALL_BEGIN + 1
    
    CELL_END = WALL_END

class PatternMatrix:
    def __init__(self, lst):
        self.val = lst if len(lst) == 9 else [0 for pos_x in range(0, 9)]

    def middle(self):
        return self.val[4]
    
    def apply1(self, func): 
        return PatternMatrix([func(self.val[i]) for i in range(0, len(self.val))])
    def apply2(self, other, func): 
        return PatternMatrix([func(self.val[i], other.val[i]) for i in range(0, len(self.val))])
    def rotate_mat(self): 
        return PatternMatrix([self.val[pos_x] for pos_x in [6,3,0,7,4,1,8,5,2]])

    def match_pattern(self, pattern_mat, match_func): 
        for i in range(0, len(self.val)):
            if not match_func(self.val[i], pattern_mat[i]):
                return False
        return True

def create_cell_func(input_pattern):    
    cell_type = input_pattern.middle()
    
    sprite = [cell_empty]

    if Cell.FOOD_BEGIN <= cell_type <= Cell.FOOD_END:
        if cell_type == Cell.FOOD_PELLET_SMALL:
            sprite.append(cell_food_small)
        elif cell_type == Cell.FOOD_PELLET_LARGE:
            sprite.append(cell_food_large)
    elif Cell.WALL_BEGIN <= cell_type <= Cell.WALL_END:
        def constrain_val(val):
            if Cell.WALL_BEGIN <= val <= Cell.WALL_END:
                return Cell.WALL_BEGIN
            else:
                return Cell.EMPTY

        pattern = input_pattern.apply1(constrain_val)

        def match_rpattern(input_matrix, pattern_matrix, func):
            def match_value(input, pattern):
                if pattern == Cell.NONE:
                    return True
                else:
                    if pattern == input: 
                        return True
                    elif pattern == Cell.WALL_BEGIN and Cell.WALL_BEGIN <= input <= Cell.WALL_END: 
                        return True
                    else:
                        return False
                return (pattern == Cell.NONE or input == pattern)
            
            t_matrix = input_matrix
            t_val = False
            
            for i in range(0, 4):
                if t_matrix.match_pattern(pattern_matrix, match_value):
                    func(i)
                    t_val = True
                t_matrix = t_matrix.rotate_mat()
            return t_val
        
        func_left_wall = cell_empty
        func_right_wall = cell_empty
        func_inner_corner = cell_empty
        func_outer_corner = cell_empty
                
        if cell_type == Cell.WALL_ROUND:
            func_left_wall    = left_wall
            func_right_wall   = right_wall
            func_inner_corner = inner_round_corner
            func_outer_corner = outer_round_corner
        elif cell_type == Cell.WALL_SQUARE:
            func_left_wall    = left_wall
            func_right_wall   = right_wall
            func_inner_corner = inner_square_corner
            func_outer_corner = outer_square_corner
        else:
            pass
            
        def create_draw_func(draw_func):
            def func(i): 
                sprite.append(rotatefunc(draw_func, TAU * i / 4))
            return func
            
        N = Cell.NONE
        E = Cell.EMPTY
        W = Cell.WALL_BEGIN
        
        match_rpattern(pattern, [N,E,N,
                                 N,W,E,
                                 N,N,N], create_draw_func(func_outer_corner))
        match_rpattern(pattern, [N,W,E,
                                 N,W,W,
                                 N,N,N], create_draw_func(func_inner_corner))
        match_rpattern(pattern, [N,W,N,
                                 E,W,N,
                                 N,N,N], create_draw_func(func_left_wall))
        match_rpattern(pattern, [N,W,N,
                                 N,W,E,
                                 N,N,N], create_draw_func(func_right_wall))
    
    return joinfunc(sprite)

class Maze:
    def __init__(self):
        self.num_cell_cols = 0
        self.num_cell_rows = 0
        
        self.pos_x = 0
        self.pos_y = 0
        
        self.maze_width = 1
        self.maze_height = 1
        self.ds = 0
        
        self.cell_val = []
        self.cell_render_func = []
        
        self.img_buffer = None

    def set_dimension(self, x, y, width, height):
        self.pos_x = x
        self.pos_y = y
        self.maze_width = width
        self.maze_height = height

    def get_min_x(self):
        return 0
    def get_min_y(self):
        return 0
    def get_max_x(self):
        return self.num_cell_cols - 1
    def get_max_y(self):
        return self.num_cell_rows - 1

    def is_valid_cell(self, i, j):
        return self.get_min_x() <= i <= self.get_max_x() and self.get_min_y() <= j <= self.get_max_y()

    def get_cell(self, i, j):
        return self.cell_val[i][j] if (0 <= i < self.num_cell_cols and 0 <= j < self.num_cell_rows) else Cell.EMPTY

    def collide_cell(self, i, j):
        cell_type = self.get_cell(i, j)

        if cell_type != None:
            if Cell.WALL_BEGIN <= cell_type <= Cell.WALL_END:
                return True
        return False
    
    def get_matrix(self, i, j):
        return PatternMatrix([(self.cell_val[pos_x][pos_y] if self.is_valid_cell(pos_x, pos_y) else 0) for pos_x in range(i-1, i+2) for pos_y in range(j-1, j+2)])

    def render_cell_to_buffer(self, i, j, buffer):
        if buffer != None:
            buffer.pushMatrix()
            buffer.translate((i + 0.5) * self.ds, (j + 0.5) * self.ds)
            buffer.rotate(TAU*0.25)
            
            buffer.fill(0)
            buffer.stroke(0, 0, 100)
            buffer.strokeWeight(self.ds/10)

            self.cell_render_func[i][j](buffer, self.ds)
            buffer.popMatrix()
            
    def render_cell(self, i, j, func):
        pushMatrix()
        translate(self.pos_x + (i + 0.5) * self.ds, self.pos_y + (j + 0.5) * self.ds)
        rectMode(RADIUS)
        ellipseMode(RADIUS)

        func(self.ds/2)
    
        popMatrix()

    def update_cell(self, i, j, val):
        if self.is_valid_cell(i, j):
            self.cell_val[i][j] = val
            
            self.img_buffer.beginDraw()
            for pos_x in range(i-1, i+2):
                for pos_y in range(j-1, j+2):
                    if self.is_valid_cell(pos_x, pos_y):
                        self.cell_render_func[pos_x][pos_y] = create_cell_func(self.get_matrix(pos_x, pos_y))
                        self.render_cell_to_buffer(pos_x, pos_y, self.img_buffer)
            self.img_buffer.endDraw()
    
    def eat_cell(self, i, j):
        cell_type = self.get_cell(i, j)
        self.update_cell(i, j, Cell.EMPTY)
        return cell_type


    def load_array(self, in_arr):
        self.num_cell_cols = len(in_arr)
        self.num_cell_rows = 0

        if self.num_cell_cols != 0:
            self.num_cell_rows = len(in_arr[0])
        
        if self.num_cell_cols != 0 and self.num_cell_rows != 0:
            for i in in_arr:            
                if self.num_cell_rows != len(i):
                    raise Exception("Maze : Non rectangular array passed")
            self.cell_val = in_arr
            
            self.cell_render_func = []
            for i in range(0, self.num_cell_cols):
                self.cell_render_func.append([])
                for j in range(0, self.num_cell_rows):
                    self.cell_render_func[-1].append(create_cell_func(self.get_matrix(i, j)))
    
            self.img_buffer = createGraphics(self.maze_width, self.maze_height)
            self.img_buffer.beginDraw()
            self.img_buffer.colorMode(RGB, 100)

            self.img_buffer.rectMode(CORNER)
            self.img_buffer.rect(0, 0, self.maze_width, self.maze_height)

            self.img_buffer.rectMode(RADIUS)
            self.img_buffer.ellipseMode(RADIUS)
            
            self.ds = float(self.maze_width)/self.num_cell_cols if self.num_cell_cols != 0 else 0

            for i in range(0, self.num_cell_cols):
                for j in range(0, self.num_cell_rows):
                    self.render_cell_to_buffer(i, j, self.img_buffer)
            self.img_buffer.endDraw()
        
    def render(self):
        if self.img_buffer != None:
            image(self.img_buffer, self.pos_x, self.pos_y, self.maze_width, self.maze_height)


window_width = 1000
window_height = 1000

class KeyBoard_Event:
    def __init__(self):
        self.key_val = [False for x in range(0, 256)]

    def press(self):
        for i in range(0, len(self.key_val)):
            if key == chr(i):
                self.key_val[i] = True

    def release(self):
        for i in range(0, len(self.key_val)):
            if key == chr(i):
                self.key_val[i] = False

    def is_pressed(self, i):
        return self.key_val[ord(i)]

class Mouse_Event:
    def __init__(self):
        self.mouse_pos = PVector(0, 0)
        self.mouse_pressed = False

    def press(self):
        self.mouse_pressed = True

    def release(self):
        self.mouse_pressed = False

    def move(self):
        self.mouse_pos = PVector(mouseX, mouseY)

keyboard = KeyBoard_Event()
mouse = Mouse_Event()

class Event:
    KEY_UP = "w"
    KEY_DOWN = "s"
    KEY_LEFT = "a"
    KEY_RIGHT = "d"
    KEY_ENTER = ENTER

    def __init__(self):
        self._keyboard = keyboard
        self._mouse = mouse

        self._key_val = []
        self._mouse_pos = PVector(0, 0)
        self._mouse_pressed = False
        self._mouse_moved = False

        self._event_time = millis()

    def poll(self):
        self._event_time = millis()
        
        self._key_val = self._keyboard.key_val

        self._mouse_moved = (self._mouse_pos != self._mouse.mouse_pos)
        self._mouse_pos = self._mouse.mouse_pos
        self._mouse_pressed = self._mouse.mouse_pressed

    def get_event_time(self):
        return (millis() - self._event_time)

    def key_is_pressed(self, i):
        if isinstance(i, list):
            for iter in i:
                if self._key_val[ord(i)]:
                    return True
            return False
        else:
            return self._key_val[ord(i)]

    def mouse_is_pressed(self):
        return self._mouse_pressed

    def mouse_moved(self):
        return self._mouse_moved

    def mouse_pos(self):
        return self._mouse_pos

class Mover:
    def __init__(self, x, y):
        self._ds = 10
        self._pos = PVector(int(x) * self._ds, int(y) * self._ds)
        self._vel = PVector(0, 0)
        self._angle = 0

    def update(self, new_vel, collision_func):
        def collide(pos):
            cell_x = int(round(pos.x/ self._ds))
            cell_y = int(round(pos.y/ self._ds))

            dx = pos.x - self._ds * cell_x
            dy = pos.y - self._ds * cell_y

            kx = 1 if (0 < dx) else (-1 if (dx < 0) else 0)
            ky = 1 if (0 < dy) else (-1 if (dy < 0) else 0)

            if dx != 0 and dy != 0:
                return True
            if collision_func(cell_x, cell_y):
                return True

            if collision_func(cell_x + kx, cell_y):
                return True
            if collision_func(cell_x, cell_y + ky):
                return True
            if collision_func(cell_x + kx, cell_y + ky):
                return True   

            return False

        new_pos = self._pos.copy()

        if new_vel != PVector(0, 0) and not collide(new_pos + new_vel):
            new_pos += new_vel
            self._vel = new_vel
        elif not collide(new_pos + self._vel):
            new_pos += self._vel
        else:
            self._vel = PVector(0, 0)

        if 0 < self._vel.x:
            self._angle = 0
        if 0 < self._vel.y:
            self._angle = TAU * 0.25
        if self._vel.x < 0:
            self._angle = TAU * 0.5
        if self._vel.y < 0:
            self._angle = TAU * 0.75

        self._pos = new_pos

    def get_draw_func(self):
        def _cell(R):
            fill(100)
            rect(0, 0, R, R)

        return _cell

    def get_pos(self):
        return PVector(self._pos.x / self._ds, self._pos.y / self._ds)

    def get_cell(self):
        return PVector(int(round(self._pos.x / self._ds)), int(round(self._pos.y / self._ds)))

class Player:
    def __init__(self, x = 1, y = 1):
        self._pos = Mover(x, y)
        self._time = 0

    def get_pos(self):
        return self._pos.get_pos()

    def get_cell(self):
        return self._pos.get_cell()

    def get_draw_func(self):
        def sprite(R):
            pushMatrix()
            fill(100, 100, 0)
            noStroke()

            total_time = 20

            if self._pos._vel != PVector(0, 0):
                self._time += 1
                self._time = self._time % total_time
            else:
                self._time = 0

            rotate(self._pos._angle)

            mouth_angle = (sin((self._time + total_time/2)* PI / total_time) ** 2) * TAU / 8

            arc(0, 0, R, R, mouth_angle, TAU - mouth_angle, PIE)
            popMatrix()

        return sprite

    def update(self, maze_state):
        new_vel = PVector(0, 0)

        if maze_state._event.key_is_pressed(Event.KEY_LEFT):
            new_vel.x = -1
        if maze_state._event.key_is_pressed(Event.KEY_RIGHT):
            new_vel.x = +1
        if maze_state._event.key_is_pressed(Event.KEY_UP):
            new_vel.y = -1
        if maze_state._event.key_is_pressed(Event.KEY_DOWN):
            new_vel.y = +1     

        cell_type = maze_state._maze.eat_cell(int(self.get_cell().x), int(self.get_cell().y))

        if cell_type == Cell.FOOD_PELLET_SMALL:
            maze_state._score += 10
        if cell_type == Cell.FOOD_PELLET_LARGE:
            maze_state._score += 50

            for i in maze_state._ghosts:
                i._state = Ghost.State.EDIBLE

        self._pos.update(new_vel, maze_state._maze.collide_cell)

    def render(self, maze_state):
        maze_state._maze.render_cell(self.get_pos().x, self.get_pos().y, self.get_draw_func())

class Ghost:
    class State:
        DEFAULT = 0
        EDIBLE = 1
        EATEN = 2

    def __init__(self, x = 1, y = 1):
        self._pos = Mover(x, y)
        self._time = 0
        self._state = Ghost.State.EATEN
        self._pos._vel = r_vel()

    def get_vel(self):
        return self._pos._vel

    def get_pos(self):
        return self._pos.get_pos()

    def get_cell(self):
        return self._pos.get_cell()

    def get_draw_func(self):
        def draw_ghost_body(R, body_color = 25, outline_color = color(0, 0)):
            stroke(outline_color)
            fill(body_color)

            beginShape()
            vertex(-R, 0)
            vertex(-R, R)
            vertex(-0.75*R, 0.75*R)
            vertex(-0.50*R, 1.00*R)
            vertex(-0.25*R, 0.75*R)
            vertex(+0.00*R, 1.00*R)
            vertex(+0.25*R, 0.75*R)
            vertex(+0.50*R, 1.00*R)
            vertex(+0.75*R, 0.75*R)
            vertex(+R, R)
            vertex(+R, 0)
            endShape()

            arc(0, 0, R, R, TAU * 0.5, TAU, OPEN)

        def draw_ghost_eyes(R, outer_color = 100, inner_color = 0):
            noStroke()
            pushMatrix()
            translate(0, -R/8)

            pushMatrix()
            translate(-0.5*R, 0)
            fill(outer_color)
            ellipse(0, 0, 0.25*R, 0.25*R)
            fill(inner_color)
            rotate(self._pos._angle)
            ellipse(R/8, 0, R/8, R/8)
            popMatrix()

            pushMatrix()
            translate(+0.5*R, 0)
            fill(outer_color)
            ellipse(0, 0, 0.25*R, 0.25*R)
            fill(inner_color)
            rotate(self._pos._angle)
            ellipse(R/8, 0, R/8, R/8)
            popMatrix()

            popMatrix()

        def draw_ghost_mouth(R, mouth_color = 0):
            pushMatrix()
            translate(0, 0.375*R)
            strokeWeight(R/5)
            stroke(mouth_color)
            noFill()     

            beginShape()
            vertex(-0.75*R, +0.125*R)
            vertex(-0.50*R, -0.125*R)
            vertex(-0.25*R, +0.125*R)
            vertex(+0.00*R, -0.125*R)
            vertex(+0.25*R, +0.125*R)
            vertex(+0.50*R, -0.125*R)
            vertex(+0.75*R, +0.125*R)
            endShape()

            popMatrix()

        sprite = lambda x : None

        if self._state == Ghost.State.DEFAULT:
            def _sprite(R):
                draw_ghost_body(R)
                draw_ghost_eyes(R)

            sprite = _sprite
        elif self._state == Ghost.State.EDIBLE:
            def _sprite(R):
                draw_ghost_body(R, color(0, 0, 100))
                draw_ghost_eyes(R, 0, 100)
                draw_ghost_mouth(R)

            sprite = _sprite
        elif self._state == Ghost.State.EATEN:
            sprite = draw_ghost_eyes

        return sprite

    def update(self, maze_state):
        pos = self.get_pos()
        self._pos.update(self.get_vel(), maze_state._maze.collide_cell)

        if pos == self.get_pos():
            self._pos._vel = r_vel()
        if self.get_pos() == self.get_cell():
            if random(0, 10) < 2:
                self._pos._vel = r_vel()

    def render(self, maze_state):
        maze_state._maze.render_cell(self.get_pos().x , self.get_pos().y, self.get_draw_func())

class MazeState:
    def __init__(self):
        self._event = Event()

        try:
            self._maze = Maze()

            k1 = int(random(10, 12))
            k2 = k1

            E = Cell.FOOD_PELLET_SMALL
            R = Cell.WALL_ROUND
            S = Cell.WALL_SQUARE
            P = Cell.FOOD_PELLET_LARGE

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

            self._maze.set_dimension(int(0.1 * width), int(0.1 * height), int(0.8 * width), int(0.8 * height))
            self._maze.load_array(arr)

            self._players = [Player(1, 1)]
            self._ghosts = [Ghost(1, 1), Ghost(1, 1)]
            
            self._score = 0
            self._no_clip = False

        except Exception as ex:
            print("Maze : " + str(ex))

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

            self.event = Event()
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

    font = createFont("RobotoMono-Thin", 100)
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