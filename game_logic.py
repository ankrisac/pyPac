import tile_map as TL

class Food(TL.SpriteEntity):
    def __init__(self):
        super(Food, self).__init__()
        self.set_sprite(0)

class Wall(TL.SpriteEntity):
    def __init__(self):
        super(Wall, self).__init__()
        self.set_sprite(1)

class Ghost(TL.SpriteEntity):
    def __init__(self):
        super(Ghost, self).__init__()
        self.pos_x = 5
        self.pos_y = 5
        
        self.set_sprite(2)

    def update(self, events):
        self.pos_x += round(random(-1, 1)) * 0.1 
        self.pos_y += round(random(-1, 1)) * 0.1 
        

class Game:
    def __init__(self):
        self.frame = TL.Frame().resize(500, 500).set_tile_scale(50, 50)

        self.renderer = TL.SpriteRenderer()
        self.renderer.add_sprite("undefined.png")
        self.renderer.add_sprite("empty.png")
        self.renderer.add_sprite("Ghost.gif")

        ghost = Ghost()

        arr = [[[Food, Wall][int(random(0, 2))]() for x in range(0, 10)] for y in range(0, 10)]
        game_map = TL.TileGrid().set_buffer(arr)

        self.frame.set_renderer(self.renderer)
        self.frame.add_child(game_map)
        self.frame.add_child(ghost)

    def update(self):
        self.frame.update()
        self.frame.render()

    def get_frame_buffer(self):
        return self.frame.get_frame_buffer()
