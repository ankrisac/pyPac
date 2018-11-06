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

class MazeRenderer(object):
    def get_min_x(self):
        return 0

    def get_min_y(self):
        return 0

    def get_max_x(self):
        return self.num_cell_cols - 1

    def get_max_y(self):
        return self.num_cell_rows - 1

    def resize(self, x, y, width, height):
        self.pos_x = x
        self.pos_y = y
        self.maze_width = width
        self.maze_height = height

    def __init__(self):
        self.num_cell_cols = 0
        self.num_cell_rows = 0
        
        self.resize(0, 0, 1, 1)
        self.ds = 0
        
        self.cell_val = []
        self.cell_render_func = []
        
        self.img_buffer = None

    def is_valid_cell(self, i, j):
        return self.get_min_x() <= i <= self.get_max_x() and self.get_min_y() <= j <= self.get_max_y()

    def get_cell(self, i, j):
        return self.cell_val[i][j] if (0 <= i < self.num_cell_cols and 0 <= j < self.num_cell_rows) else Cell.EMPTY
    
    def get_matrix(self, i, j):
        return PatternMatrix([(self.cell_val[pos_x][pos_y] if self.is_valid_cell(pos_x, pos_y) else 0) for pos_x in range(i-1, i+2) for pos_y in range(j-1, j+2)])

    def update_cell(self, i, j, val):
        def draw_cell(i, j, buffer):
            if buffer != None:
                buffer.pushMatrix()
                buffer.translate((i + 0.5) * self.ds, (j + 0.5) * self.ds)
                buffer.rotate(TAU*0.25)
                
                buffer.fill(0)
                buffer.stroke(0, 0, 100)
                buffer.strokeWeight(self.ds/10)

                self.cell_render_func[i][j](buffer, self.ds)
                buffer.popMatrix()

        if self.is_valid_cell(i, j):
            self.cell_val[i][j] = val
            
            self.img_buffer.beginDraw()
            for pos_x in range(i-1, i+2):
                for pos_y in range(j-1, j+2):
                    if self.is_valid_cell(pos_x, pos_y):
                        self.cell_render_func[pos_x][pos_y] = create_cell_func(self.get_matrix(pos_x, pos_y))
                        draw_cell(pos_x, pos_y, self.img_buffer)
            self.img_buffer.endDraw()

    def update_buffer(self, in_arr):
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
                    self.update_cell(i, j, self.img_buffer)
            self.img_buffer.endDraw()
        
    def collide_cell(self, i, j):
        cell_type = self.get_cell(i, j)

        if cell_type != None:
            if Cell.WALL_BEGIN <= cell_type <= Cell.WALL_END:
                return True
        return False

    def eat_cell(self, i, j):
        cell_type = self.get_cell(i, j)
        self.update_cell(i, j, Cell.EMPTY)
        return cell_type
    
    def render_entity(self, i, j, func):
        pushMatrix()
        translate(self.pos_x + (i + 0.5) * self.ds, self.pos_y + (j + 0.5) * self.ds)
        rectMode(RADIUS)
        ellipseMode(RADIUS)

        func(self.ds/2)
    
        popMatrix()

    def render(self):
        if self.img_buffer != None:
            image(self.img_buffer, self.pos_x, self.pos_y, self.maze_width, self.maze_height)
