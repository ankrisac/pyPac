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

class Sprite(object):
    RASTER = 0
    VECTOR = 1
    
    def __init__(self):
        self.sprite = None
        self.type = Sprite.VECTOR 
        
    def render(self, buffer, x, y, w, h):
        if self.type == Sprite.VECTOR:
            buffer.shape(self.sprite, x, y, w, h)
        elif self.type == Sprite.RASTER:
            buffer.image(self.sprite, x, y, w, h)
            
    def set_vector(self, pshape):
        self.sprite = pshape
        self.type = Sprite.VECTOR
        return self
        
    def set_image(self, sprite):
        self.sprite = sprite
        self.type = Sprite.RASTER
        return self
        
    def load_sprite(self, path):
        path_split = path.split(".")
        if len(path_split) == 2:
            ext = path_split[1]
            
            if ext == "svg" or ext == "obj":
                self.sprite = loadShape(path)
                self.type = Sprite.VECTOR
            elif ext == "png" or ext == "jpg" or ext == "gif":
                self.sprite = loadImage(path)
                self.type = Sprite.RASTER
        return self

class SpriteRenderer(object):
    def __init__(self):
        self._width = 10
        self._height = 10

        self._sprites = []
        self._undefined = Sprite().load_sprite("undefined.png")
        
    def add_sprite(self, path):
        self._sprites.append(Sprite().load_sprite(path))

    def set_sprite_scale(self, w, h):
        self._width = w
        self._height = h
        return self
    
    def get_width(self):
        return self._width
    
    def get_height(self):
        return self._height

    def render_sprite(self, buffer, sprite_id):
        if sprite_id != None and sprite_id < len(self._sprites):
            self._sprites[sprite_id].render(buffer, 0, 0, self._width, self._height)   
        else:
            self._undefined.render(buffer, 0, 0, self._width, self._height)

class Entity(object):
    def __init__(self):
        self.set_pos(0, 0)
        self.set_angle(0)

    def set_pos(self, x, y):
        self.pos_x = x
        self.pos_y = y
        return self

    def set_angle(self, angle):
        self.angle = angle
        return self

    def render(self, buffer, sprite_renderer):
        return self
    
    def update(self, events):
        return self

class SpriteEntity(Entity):
    def __init__(self):
        super(SpriteEntity, self).__init__()
        self.set_sprite(None)

    def set_sprite(self, sprite_id):
        self.sprite_id = sprite_id
        return self

    def render(self, buffer, sprite_renderer):
        buffer.pushMatrix()
        buffer.translate(self.pos_x, self.pos_y)
        buffer.rotate(self.angle)
        sprite_renderer.render_sprite(buffer, self.sprite_id)
        buffer.popMatrix()
        return self

class TileGrid(Entity):
    def __init__(self):
        super(TileGrid, self).__init__()
        self.set_buffer([])

    def get_tile(self, x, y):
        if 0 <= x < self._max_cols and 0 <= y < self._max_rows:
            return self._buffer[y][x]
        else:
            return None

    def set_tile(self, x, y, val):
        if 0 <= x < self._max_cols and 0 <= y < self._max_rows:
            self._buffer[y][x] = val
            val.set_pos(x, y)
        return self

    def set_buffer(self, buffer):
        max_rows = len(buffer)
        max_cols = 0
        
        if max_rows != 0:     
            max_cols = len(buffer[0])
            
            for i in buffer:
                if max_cols != len(i):
                    raise Exception("TilGrid Err : Args - Non Rectangular Buffer")
                    
        self._max_rows = max_rows
        self._max_cols = max_cols
        
        self._buffer = buffer
        
        y = 0
        for i in self._buffer:
            x = 0
            for j in i:
                j.set_pos(x, y)
                x += 1
            y += 1
        return self
        
    def render(self, buffer, sprite_renderer):
        buffer.pushMatrix()
        buffer.translate(self.pos_x, self.pos_y)
        buffer.rotate(self.angle)
        for i in self._buffer:
            for j in i:
                j.render(buffer, sprite_renderer)
        buffer.popMatrix()

    def update(self, events):
        for i in self._buffer:
            for j in i:
                j.update(events)

class Frame(object):
    def __init__(self):
        self._renderer = SpriteRenderer()
        self.set_child_entities([])

    def set_renderer(self, renderer):
        self._renderer = renderer

    def get_frame_buffer(self):
        return self._frame_buffer

    def resize(self, width, height):
        self._width = width
        self._height = height
        self._frame_buffer = createGraphics(int(self._width), int(self._height), P3D)
        return self

    def set_tile_scale(self, tile_width, tile_height):
        self._tile_width = tile_width
        self._tile_height = tile_height
        return self

    def set_child_entities(self, lst):
        self._child_entities = lst

    def add_child(self, child):
        self._child_entities.append(child)

    def render(self):
        if self._frame_buffer != None:
            self._frame_buffer.hint(DISABLE_TEXTURE_MIPMAPS)
            self._frame_buffer.textureSampling(3)
            self._frame_buffer.noSmooth()
            
            self._frame_buffer.beginDraw()
            self._frame_buffer.colorMode(RGB, 100)
            self._frame_buffer.shapeMode(CENTER)
            self._frame_buffer.rectMode(RADIUS)
            self._frame_buffer.ellipseMode(RADIUS)
            self._frame_buffer.background(0)
            self._frame_buffer.scale(self._tile_width, self._tile_height)
        
            self._renderer.set_sprite_scale(1, 1)
        
            for i in self._child_entities:
                i.render(self._frame_buffer, self._renderer)
            self._frame_buffer.endDraw()
    
    def update(self):
        for i in self._child_entities:
            i.update(None)