import time
import tile_map as TL
import events as Ev
import copy
import random

class NoneEntity(TL.Entity):
    pass

class Tile(TL.Entity):
    pass

class TileUndefined(Tile):
    def __init__(self):
        super(TileUndefined, self).__init__()
        self.set_sprite(TL.load_sprite("sprites/undefined.png"))

class TileEmpty(Tile):
    def __init__(self):
        super(TileEmpty, self).__init__()
        self.set_sprite(TL.load_sprite("sprites/wall/empty.png"))

class TileFood(Tile):
    def __init__(self):
        super(TileFood, self).__init__()
        self.set_sprite(TL.load_sprite("sprites/food/food.png"))
        
class TilePowerPellet(TileFood):
    def __init__(self):
        super(TilePowerPellet, self).__init__()
        self.set_sprite(TL.load_sprite("sprites/food/powerpellet.png"))
    
class TileWall(Tile):
    def __init__(self):
        super(TileWall, self).__init__()
        self.set_sprite(TL.load_sprite("sprites/wall/wall.png"))

class Mover(TL.Entity):
    def __init__(self, parent):
        super(Mover, self).__init__()
        self.pos_x = 0
        self.pos_y = 0
        
        self._vel_x = 0
        self._vel_y = 0
        
        self._old_vel_x = 0
        self._old_vel_y = 0
        
        self.parent = parent
        self.moved = False
        
    def set_vel(self, x, y):
        self._old_vel_x = self._vel_x
        self._old_vel_y = self._vel_y
        
        self._vel_x = x
        self._vel_y = y
        
    def update(self):
        def collide(x, y):
            def is_empty(x, y):
                type = self.parent.maze.get_tile(int(x), int(y))
                
                if type != None:
                    return not isinstance(self.parent.maze.get_tile(int(x), int(y)), TileWall)
                else:
                    return False
        
            r = 0.1
        
            x1 = floor(x+r)
            x2 = ceil(x-r)
            
            y1 = floor(y+r)
            y2 = ceil(y-r)
            
            if is_empty(x1, y1) and is_empty(x1, y2) and is_empty(x2, y1) and is_empty(x2, y2):
                return False
        
            return True
        
        def try_to_move(vx, vy):
            x = self.pos_x
            y = self.pos_y 
            px = x + vx
            py = y + vy
            if not collide(px, py):
                self.pos_x = px
                self.pos_y = py
            elif not collide(px, y):
                self.pos_x = px
                self.pos_y = y
            elif not collide(x, y):
                self.pos_x = x
                self.pos_y = py
            else:
                return False
            return True

        if not try_to_move(self._vel_x, self._vel_y):
            if not try_to_move(self._old_vel_x, self._old_vel_y):
                self.moved = True
            else:
                self.moved = True
        else:
            self.moved = True

class Player(Mover):
    def __init__(self, parent):
        super(Player, self).__init__(parent)
        self.parent = parent
        self.pos_x = 0
        self.pos_y = 0
        
        self.player_vel = 0.15

        self.move_animation = TL.load_sprite_animation("sprites/player").set_length(250)
        self.current_frame = 0

        self.death_animation = TL.load_sprite_animation("sprites/player_death").set_length(5000)
        self.death_animation.loop = False

        self.is_alive = True

        self.set_sprite(self.move_animation)
        self.update = self.updatefn_move
        
        self.t = 0

        self.powered_up = False

    def input_motion(self, x, y):
        self.set_vel(x * self.player_vel, y * self.player_vel)

    def updatefn_move(self):
        super(Player, self).update()
        self.set_angle(HALF_PI - atan2(self._vel_x, self._vel_y))

        for i in self.parent.ghosts:
            if round(i.pos_x) == round(self.pos_x) and round(i.pos_y) == round(self.pos_y):
                self.set_angle(0)

                self.death_animation.reset()
                self.set_angle(0)
                self.parent.stop_all_sounds()
                self.parent.sound_death.play()

                self.update = self.updatefn_die
                self.set_sprite(self.death_animation)
                self.parent.update = self.parent.updatefn_gameover

        cell = self.parent.maze.get_tile(round(self.pos_x), round(self.pos_y))

        if isinstance(cell, TileFood):
            self.parent.maze.set_tile(round(self.pos_x), round(self.pos_y), TileEmpty())

            if isinstance(cell, TilePowerPellet):
                self.powered_up = True
                for i in self.parent.ghosts:
                    i.power_down()
        

            if not self.parent.sound_chomp.isPlaying():
                self.parent.sound_chomp.loop(1)

    def updatefn_die(self):
        pass

def search_dijkstra(x, y, max_rows, max_cols, get_adj_node):
    path_matrix = [[None for i in range(0, max_cols)] for j in range(0, max_rows)]
    
    def iterate_search(iter_set):
        next_cells = []
    
        for (i, j) in iter_set:
            adj_cell = get_adj_node(i, j)
    
            for (m, n) in adj_cell:
                if path_matrix[m][n] == None:
                    path_matrix[m][n] = (i, j)
                    next_cells.append((m, n))
    
        return list(set(next_cells))

    path_matrix[x][y] = (0, 0)
    iter_set = [(x, y)]

    while iter_set != []:
        iter_set = iterate_search(iter_set)

    return path_matrix

class Ghost(Mover):
    def __init__(self, parent):
        super(Ghost, self).__init__(parent)
        self.parent = parent
        self.pos_x = 0
        self.pos_y = 0
        self.ghost_vel = 0.05
        
        (self.next_x, self.next_y) = (0, 0)

        self.set_sprite(TL.load_sprite("sprites/ghost.png"))

    def update(self):
        super(Ghost, self).update()

        (c, r) = (self.parent.maze.get_max_cols(), self.parent.maze.get_max_rows())
        (px, py) = (int(round(self.parent.player.pos_x)), int(round(self.parent.player.pos_y)))         

        def adj_get(i, j):
            adj_node = []

            for (di, dj) in [(-1, 0), (+1, 0), (0, -1), (0, +1)]:
                (I, J) = (i + di, j + dj)

                if 0 <= I < c and 0 <= J < r and not isinstance(self.parent.maze.get_tile(I, J), TileWall):
                    adj_node.append((I, J))

            return adj_node

        path_matrix = search_dijkstra(px, py, c, r, adj_get)

        (dx, dy) = (abs(round(self.pos_x) - self.next_x), abs(round(self.pos_y) - self.next_y))
        
        if (dx < 0.01 or 1 <= dx) and (dy < 0.5 or 1 <= dy):
            (self.next_x, self.next_y) = path_matrix[int(round(self.pos_x))][int(round(self.pos_y))]
                    
        (Dx, Dy) = (self.next_x - self.pos_x, self.next_y - self.pos_y)

        h = sqrt(Dx*Dx + Dy*Dy)

        (Dx, Dy) = (Dx/h, Dy/h)
        self.set_vel(Dx * 0.1, Dy * 0.1)

    def power_down(self):
        self.set_sprite(TL.load_sprite("sprites/undefined.png"))
        self.update = lambda: None

class PacMan(object):
    def __init__(self, minim):
        self.minim = minim
        self.renderer = TL.SpriteRenderer()
        
        self.loadMap("map1.mz")
        self.load_sounds()

        self.frame.render()
        self.update = self.updatefn_init
        self.sound_intro.play()

        self.t = 0

    def loadMap(self, path):
        EMPTY = " "
        WALL = "#"
        FOOD = "+"
        POWERPELLET = "-"
        PLAYER = "P"
        GHOST = "G"

        file = open(path, "r")

        self.player = Player(self).set_pos(1, 1)
        self.ghosts = []

        x = 0
        y = 0
        arr = []
        for i in file.readlines():
            elem = i.replace("\n", "").split(";")

            x = 0
            row = []
            for j in elem:
                cell = TileUndefined()

                if j == PLAYER or j == GHOST:
                    if j == PLAYER:
                        self.player.set_pos(x, y)
                    if j == GHOST:
                        self.ghosts.append(Ghost(self).set_pos(x, y))
                    cell = TileEmpty()
                elif j == EMPTY:
                    cell = TileEmpty()
                elif j == WALL:
                    cell = TileWall()
                elif j == FOOD:
                    cell = TileFood()
                elif j == POWERPELLET:
                    cell = TilePowerPellet()

                row.append(cell)

                x += 1
            arr.append(row)
            y += 1

        file.close()

        self.maze = TL.TileGrid().set_buffer(arr)

        n = 100
        k = max(self.maze.get_max_cols(), self.maze.get_max_rows()) + 1
        self.frame = TL.Frame().resize(n * k, n * k).set_tile_scale(n, n).set_pos(0.5, 0.5)
        self.frame.set_renderer(self.renderer)

        for i in [self.maze] + self.ghosts + [self.player]:
            self.frame.add_child(i)

    def quit_game(self):
        self.stop_all_sounds()

    def load_sounds(self):
        self.sound_intro = self.minim.loadFile("sounds/beginning.wav")
        self.sound_chomp = self.minim.loadFile("sounds/chomp.wav")
        self.sound_death = self.minim.loadFile("sounds/death.wav")
        self.sound_eatfruit = self.minim.loadFile("sounds/eatfruit.wav")
        self.sound_extrapac = self.minim.loadFile("sounds/extrapac.wav")
        self.sound_intermission = self.minim.loadFile("sounds/intermission.wav")

    def stop_all_sounds(self):
        self.sound_intro.pause()
        self.sound_chomp.pause()
        self.sound_death.pause()
        self.sound_eatfruit.pause()
        self.sound_extrapac.pause()
        self.sound_intermission.pause()

    def updatefn_init(self, event):
        if not self.sound_intro.isPlaying() or event.any_key_pressed():
            self.update = self.updatefn_game
            self.stop_all_sounds()

    def updatefn_paused(self, event):
        if event.key_is_pressed(Ev.Key.ESCAPE):
            self.update = self.updatefn_game

    def updatefn_gameover(self, event):
        pass

    def updatefn_game(self, event):
        t = millis()
        if t - self.t > 10:
            self.t = t
            
            x = 0
            y = 0
            
            if event.key_is_pressed("a"):
                x = -1
            elif event.key_is_pressed("d"):
                x = +1
            if event.key_is_pressed("w"):
                y = -1
            elif event.key_is_pressed("s"):
                y = +1
            elif event.key_is_pressed(Ev.Key.ESCAPE):
                self.update = self.updatefn_paused
    
            if x != 0 and y != 0:
                x /= sqrt(2)
                y /= sqrt(2)
            if x != 0 or y != 0:
                self.player.input_motion(x, y)                
    
            self.frame.update()
            self.frame.render()

    def get_frame_buffer(self):
        return self.frame.get_frame_buffer()
