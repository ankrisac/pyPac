import os
from util import Vec
import util

class Sprite(object):
    def __init__(self):
        pass

    def render(self, buffer, x, y, w, h):
        pass

class SpriteEntity(Sprite):
    UNDEFINED = 0
    RASTER = 1
    VECTOR = 2
    
    def __init__(self):
        self.sprite = None
        self.type = SpriteEntity.UNDEFINED
        
    def render(self, buffer, x, y, w, h):
        if self.type == SpriteEntity.VECTOR:
            buffer.shape(self.sprite, x, y, w, h)
        elif self.type == SpriteEntity.RASTER:
            buffer.image(self.sprite, x, y, w, h)
            
    def set_vector(self, pshape):
        self.sprite = pshape
        self.type = SpriteEntity.VECTOR
        return self
        
    def set_image(self, sprite):
        self.sprite = sprite
        self.type = SpriteEntity.RASTER
        return self

class SpriteGroup(Sprite):
    def __init__(self):
        self._sprites = []
        self._current_frame = 0

    def render(self, buffer, x, y, w, h):
        if 0 < len(self._sprites):
            self._sprites[self._current_frame].render(buffer, x, y, w, h)
        return self

    def set_sprite(self, i):
        self._current_frame = i if 0 < self._current_frame < len(self._sprites) else 0
        return self

    def get_num_sprites(self):
        return len(self._sprites)

    def next_sprite(self):
        self._current_frame += 1

        if self._current_frame == (len(self._sprites) - 1):
            self._current_frame = 0
            return self

    def is_begin(self):
        return self._current_frame == 0

    def is_end(self):
        return self._current_frame == (len(self._sprites) - 2)

class SpriteAnimation(Sprite):
    def __init__(self):
        self._sprites = []

        self.reset()
        self.set_length()
        self.loop = True

    def reset(self):
        self._t = millis()
        return self

    def set_length(self, t = 1000):
        self._max_t = t
        return self

    def render(self, buffer, x, y, w, h):
        t_diff = ((millis() - self._t)/float(self._max_t))

        if self.loop:
            t_diff = t_diff % 1
        elif t_diff >= 1:
            t_diff = 1

        self._sprites[int(round(t_diff * (len(self._sprites) - 1)))].render(buffer, x, y, w, h)
        return self

def load_sprite(path):
    if os.path.exists(path):
        out_sprite = SpriteEntity()

        path_split = path.split(".")
        if len(path_split) == 2:
            ext = path_split[1]
            
            if ext == "svg" or ext == "obj":
                out_sprite.sprite = loadShape(path)
                out_sprite.type = SpriteEntity.VECTOR
            elif ext == "png" or ext == "jpg" or ext == "gif":
                out_sprite.sprite = loadImage(path)
                out_sprite.type = SpriteEntity.RASTER

        return out_sprite
    else:
        raise Exception("Failed to Find Path : " + path)
        return SpriteEntity()

def load_sprite_animation(folder):
    animation = SpriteAnimation()

    if os.path.isdir(folder):
        _dir = os.listdir(folder)

        animation._sprites = []
        for i in _dir:
            full_path = os.path.join(folder, i)

            if os.path.isfile(full_path):
                animation._sprites.append(load_sprite(full_path))

    return animation

class SpriteRenderer(object):
    def __init__(self):
        self._width = 10
        self._height = 10
        self._undefined = load_sprite("sprites/pacman/wall/empty.png")

    def set_sprite_scale(self, w, h):
        self._width = w
        self._height = h
        return self
    
    def get_width(self):
        return self._width
    
    def get_height(self):
        return self._height

    def render_sprite(self, buffer, sprite):
        if sprite != None:
            sprite.render(buffer, 0, 0, self._width, self._height)
        elif self._undefined != None:
            self._undefined.render(buffer, 0, 0, self._width, self._height)

class Entity(object):
    def __init__(self):
        self.set_pos()
        self.set_angle()
        self.set_sprite()

    def set_pos(self, pos = Vec(0, 0)):
        self.pos = pos
        return self

    def set_angle(self, angle = 0):
        self.angle = angle
        return self
    
    def set_sprite(self, sprite = None):
        self.sprite = sprite
        return self
    
    def update(self):
        return self

    def render(self, buffer, sprite_renderer):
        buffer.pushMatrix()
        buffer.translate(self.pos.x + 0.5, self.pos.y + 0.5)
        buffer.rotate(self.angle)
        buffer.translate(-0.5, -0.5)

        sprite_renderer.render_sprite(buffer, self.sprite)
        
        buffer.popMatrix()
        return self

class TileGrid(Entity):
    def __init__(self):
        super(TileGrid, self).__init__()
        self.set_buffer([])

    def get_max_rows(self):
        return self._max_rows

    def get_max_cols(self):
        return self._max_cols

    def get_tile(self, pos):
        if 0 <= pos.x < self._max_cols and 0 <= pos.y < self._max_rows:
            return self._tile_buffer[int(pos.y)][int(pos.x)]
        return None

    def set_tile(self, pos, val):
        if 0 <= pos.x < self._max_cols and 0 <= pos.y < self._max_rows:
            self._tile_buffer[int(pos.y)][int(pos.x)] = val
        return self

    def set_buffer(self, buffer):
        max_rows = len(buffer)
        max_cols = 0
        
        if max_rows != 0:     
            max_cols = len(buffer[0])

            for i in buffer:
                max_cols = max(max_cols, len(i))
                    
        self._max_rows = max_rows
        self._max_cols = max_cols
        
        self._tile_buffer = buffer
        
        y = 0
        for i in self._tile_buffer:
            x = 0
            for j in i:
                j.set_pos(Vec(x, y))
                x += 1
            y += 1
        
        return self
        
    def render(self, buffer, sprite_renderer):
        buffer.pushMatrix()
        buffer.translate(self.pos.x, self.pos.y)
        for i in self._tile_buffer:
            for j in i:
                j.render(buffer, sprite_renderer)
        buffer.popMatrix()

    def update(self):
        for i in self._tile_buffer:
            for j in i:
                j.update()

class Frame(object):
    def __init__(self):
        self.renderer = SpriteRenderer()

        self.set_child_entities([])
        
        self.set_tile_scale()
        self.set_pos()

    def set_renderer(self, renderer):
        self.renderer = renderer
        return self

    def get_frame_buffer(self):
        return self._frame_buffer

    def resize(self, width, height):
        self._width, self._height = (width, height)
        self._frame_buffer = createGraphics(int(self._width), int(self._height), P3D)
        return self

    def set_pos(self, pos = Vec(0, 0)):
        self.pos = pos
        return self

    def set_tile_scale(self, tile_width = 1, tile_height = 1):
        self.tile_width, self.tile_height = (tile_height, tile_height)
        return self

    def set_child_entities(self, lst):
        self.child_entities = lst
        return self

    def add_child(self, child):
        self.child_entities.append(child)
        return self

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
            self._frame_buffer.scale(self.tile_width, self.tile_height)
            self._frame_buffer.translate(self.pos.x, self.pos.y)
        
            self.renderer.set_sprite_scale(1, 1)
            
            for i in self.child_entities:
                if i != None:
                    i.render(self._frame_buffer, self.renderer)

            self._frame_buffer.endDraw()
        return self

    def update(self):
        for i in self.child_entities:
            i.update()
        return self
