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

class PatternMatrix:
    def __init__(self, lst):
        if len(lst) == 9:
            self.val = lst
        else:
            self.val = [0 for i in range(0, 9)]

    def middle(self):
        return self.val[4]
    
    def apply1(self, func): 
        lst = []
        for i in range(0, len(self.val)):
            lst.append(func(self.val[i]))

        return PatternMatrix(lst)

    def apply2(self, other, func): 
        lst = []
        for i in range(0, len(self.val)):
            lst.append(func(self.val[i], other.val[i]))

        return PatternMatrix(lst)

    def rotate_mat(self): 
        return PatternMatrix([self.val[pos_x] for pos_x in [6,3,0,7,4,1,8,5,2]])

    def match_pattern(self, pattern_mat, match_func): 
        for i in range(0, len(self.val)):
            if not match_func(self.val[i], pattern_mat[i]):
                return False
        return True

def create_tile_sprite(input_pattern):    
    tile = input_pattern.middle()

    return Empty()

    if tile == Cell.FOOD_PELLET_SMALL: 
        return cell_food_small
    elif tile == Cell.FOOD_PELLET_LARGE: 
        return cell_food_large
    elif Cell.WALL_END <= tile <= Cell.WALL_END:
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
        
        sprite_left_wall = cell_empty
        sprite_right_wall = cell_empty
        sprite_inner_corner = cell_empty
        sprite_outer_corner = cell_empty
                
        if tile == Cell.WALL_ROUND:
            sprite_left_wall    = left_wall
            sprite_right_wall   = right_wall
            sprite_inner_corner = inner_round_corner
            sprite_outer_corner = outer_round_corner
        elif tile == Cell.WALL_SQUARE:
            sprite_left_wall    = left_wall
            sprite_right_wall   = right_wall
            sprite_inner_corner = inner_square_corner
            sprite_outer_corner = outer_square_corner
            
        out_sprite = []
            
        def create_sprite_renderer(sprite):
            def sprite_renderer(i): 
                out_sprite.append(rotatefunc(sprite, TAU * (i+1) / 4))
            return sprite_renderer
            
        N = Cell.NONE
        E = Cell.EMPTY
        W = Cell.WALL_BEGIN
        
        match_rpattern(pattern, [N,E,N,N,W,E,N,N,N], create_sprite_renderer(sprite_outer_corner))
        match_rpattern(pattern, [N,W,E,N,W,W,N,N,N], create_sprite_renderer(sprite_inner_corner))
        match_rpattern(pattern, [N,W,N,E,W,N,N,N,N], create_sprite_renderer(sprite_left_wall))
        match_rpattern(pattern, [N,W,N,N,W,E,N,N,N], create_sprite_renderer(sprite_right_wall))
    
        return joinfunc(out_sprite)
    elif tile == Cell.EMPTY: 
        return cell_empty
    else: 
        return cell_none 

def load_file(file, sep = '\n'):
    reader = createReader(file)
    output = ""
    
    while(True):
        ln = reader.readLine()
        if ln != None:
            output += ln + sep
        else:
            break
    
    return output

class TileConstructor(object):
    def createTile(id, type):
        if type == 0:
            return Tile(None, 0)
        else:
            raise Exception("Invalid Tile Type <" + str(type) + ">")

def parse_tile_data(tile_data):
    _row_sep = "\n"
    _tile_sep = ";"
    _tile_attrib_sep = ","
    
    try:
        print(tile_data)
        attribs = tile_data.split(_tile_attrib_sep)

        
        id = 0
        type = 0
        
        for i in attribs:
            components = i.split("=")
            
            if len(components) == 2:
                name = components[0]
                val = components[1]
                
                if name == "id":
                    id = int(val)
                elif name == "type":
                    type = int(val)
                else:
                    raise Exception("MapLoader Err: Invalid Tile Attribute <" + name + ">")
            else:
                raise Exception("MapLoader Err: Invalid Tile Attribute Syntax : " + str(len(components) - 1) + " extra '=' have been passed")
    except Exception as ex:
        raise Exception("Tile Err : " + str(ex))
    
    return TileConstructor.createTile(id, type)

def parse_map_data(map_data):
    _row_sep = "\n"
    _tile_sep = ";"
    _tile_attrib_sep = ","
    
    map_rows = map_data.split(_row_sep)
    t_map = []
    y = 0
    
    for i in map_rows:
        tiles = i.split(_tile_sep)
        t_row = []
        for j in tiles:
            t_row.append(parse_tile_data(j.split(_tile_attrib_sep)))
        t_map.append(t_row)
            
    return t_map

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

class Mover(object):
    def __init__(self, x, y):
        self._ds = 10
        self._pos = PVector(int(x) * self._ds, int(y) * self._ds)
        self._vel = PVector(0, 0)
        self._angle = 0

    def get_vel(self):
        return self._vel

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

class Player(Mover):
    def __init__(self, x, y):
        super(Player, self).__init__(x, y)
        self._time = 0

    def get_draw_func(self):
        def sprite(R):
            pushMatrix()
            fill(100, 100, 0)
            noStroke()

            total_time = 20

            if self._vel != PVector(0, 0):
                self._time += 1
                self._time = self._time % total_time
            else:
                self._time = 0

            rotate(self._angle)

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

class Ghost(Mover):
    class State:
        DEFAULT = 0
        EDIBLE = 1
        EATEN = 2

    def __init__(self, x = 1, y = 1):
        super(Ghost, self).__init__()
        self._time = 0
        self._state = Ghost.State.EATEN
        self._pos._vel = r_vel()

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
