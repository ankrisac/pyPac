
import time
import tile_map as TL
import events as Ev
import copy
import random
import math
from util import Vec
import util

def create_dijkstra_search_function(mapping_function):
    def search_func(search_list, max_cols, max_rows, get_adj_node):
        path_matrix = [[None for i in range(0, max_cols)] for j in range(0, max_rows)]

        def iterate_search(iter_set):
            next_cells = []

            for (i, j) in iter_set:
                mapping_function(get_adj_node, path_matrix, next_cells, i, j)

            return list(set(next_cells))

        iter_set = copy.copy(search_list)
        for (i, j) in search_list:
            path_matrix[i][j]

        while iter_set != []:
            iter_set = iterate_search(iter_set)

        return path_matrix
    return search_func

def dijkstra_mapping(get_adj_node, path_matrix, next_cells, i, j):
    for (m, n) in get_adj_node(i, j):
        if path_matrix[m][n] == None :
            path_matrix[m][n] = (i, j)
            next_cells.append((m, n))

def dijkstra_mapping_reverse(get_adj_node, path_matrix, next_cells, i, j):
    path_matrix[i][j] = []
    for (m, n) in get_adj_node(i, j):
        if path_matrix[m][n] is None:
            path_matrix[i][j].append((m, n))
            next_cells.append((m, n))

search_dijkstra = create_dijkstra_search_function(dijkstra_mapping)
search_dijkstra_reverse = create_dijkstra_search_function(dijkstra_mapping_reverse)

def get_path(path):
    return "sprites/pacman/" + path

class NoneEntity(TL.Entity):
    pass

class Tile(TL.Entity):
    def __init__(self):
        super(Tile, self).__init__()
        self.score_value = 0
    
    def is_wall(self):
        return False

    def eat(self):
        pass

class TileUndefined(Tile):
    Sprite = TL.load_sprite(get_path("wall/empty.png"))

    def __init__(self):
        super(TileUndefined, self).__init__()
        self.set_sprite(TileUndefined.Sprite)

class TileEmpty(Tile):
    Sprite = TL.load_sprite(get_path("wall/empty.png"))

    def __init__(self):
        super(TileEmpty, self).__init__()
        self.set_sprite(TileEmpty.Sprite)

class TileFood(Tile):
    Sprite = TL.load_sprite(get_path("food/food.png"))

    def __init__(self):
        super(TileFood, self).__init__()
        self.score_value = 10
        self.set_sprite(TileFood.Sprite)

class TilePowerPellet(TileFood):
    Sprite = TL.load_sprite(get_path("food/powerpellet.png"))

    def __init__(self):
        super(TilePowerPellet, self).__init__()
        self.score_value = 50
        self.set_sprite(TilePowerPellet.Sprite)

class TileWall(Tile):
    Sprite = TL.load_sprite(get_path("wall/wall.png"))

    def __init__(self):
        super(TileWall, self).__init__()
        self.set_sprite(TileWall.Sprite)
        
    def is_wall(self):
        return True

class Maze(TL.TileGrid):
    def get_tile(self, pos):
        tile = super(Maze, self).get_tile(pos)
        if tile != None:
            return tile
        else:
            return TileUndefined()

    def set_tile(self, pos, tile):
        super(Maze, self).set_tile(pos, tile)

    def is_wall(self, pos):
        tile = super(Maze, self).get_tile(pos)
        if tile != None:
            return tile.is_wall()
        return True

    def get_adj_nodes(self, x, y):
        adj_node = []

        for (i, j) in [(-1, 0), (+1, 0), (0, -1), (0, +1)]:
            if not self.is_wall(Vec(x + i, y + j)):
                adj_node.append((x + i, y + j))

        return adj_node

class Mover(TL.Entity):
    def __init__(self, parent):
        super(Mover, self).__init__()
        self.parent = parent

        self.pos = Vec(0, 0)
        self.vel = Vec(0, 0)
        self.pvel = Vec(0, 0)
        
    def set_vel(self, vel):
        self.pvel = self.vel
        self.vel = vel
    
    def collide(self, pos):
        r = 0.1

        is_wall = lambda x: self.parent.get_maze().is_wall(x)

        p1 = (pos + Vec(r, r)).apply(math.floor)
        p2 = (pos - Vec(r, r)).apply(math.ceil)
        return (is_wall(p1) or is_wall(p2) or is_wall(Vec(p1.x, p2.y)) or is_wall(Vec(p2.x, p1.y)))

    def try_to_move(self, vel):
        vx = Vec(vel.x, 0)
        vy = Vec(0, vel.y)

        if not self.collide(self.pos + vx + vy):
            self.pos += vx + vy
        elif not self.collide(self.pos + vx):
            self.pos += vx
        elif not self.collide(self.pos + vy):
            self.pos += vy
        else:
            return True
        return False

    def update(self):
        if not self.try_to_move(self.vel):
            self.try_to_move(self.pvel)

class Player(Mover):
    def __init__(self, parent):
        super(Player, self).__init__(parent)
        self.score = 0
        self.player_vel = 0.10

        self.move_animation = TL.load_sprite_animation(get_path("player")).set_length(250)
        self.death_animation = TL.load_sprite_animation(get_path("player_death")).set_length(500)
        self.death_animation.loop = False

        self.is_alive = True

        self.set_sprite(self.move_animation)
        self.update = self.updatefn_move
        
        self.t = 0

        self.powered_up = False

    def set_vel(self, vel):
        if vel.mag_manhattan() != 0:
            super(Player, self).set_vel(vel.norm() * self.player_vel)

    def updatefn_move(self):
        super(Player, self).update()
        self.set_angle(self.vel.angle())

        cell = self.parent.get_maze().get_tile(self.pos)

        if isinstance(cell, TileFood):
            self.score += cell.score_value
            
            self.parent.maze.set_tile(self.pos, TileEmpty())
            
            if isinstance(cell, TilePowerPellet):
                self.parent.power_up()
                
            if not self.parent.sound_chomp.isPlaying():
                self.parent.sound_chomp.loop(1)
            cell.eat()

    def get_eaten(self):
        self.parent.stop_all_sounds()
        self.parent.sound_death.play()

        self.update = lambda: None
        self.death_animation.reset()
        self.set_sprite(self.death_animation)
        self.get_eaten = lambda: None

class Ghost(Mover):
    dir_path = ["right", "up", "left", "down"]
    Sprite_Eyes = [TL.load_sprite(get_path("eyes/eyes_" + i + ".png")) for i in dir_path]
    Sprite_Retreat = [TL.load_sprite_animation(get_path("chase_" + i)).set_length(500) for i in dir_path]
    
    def __init__(self, parent):
        super(Ghost, self).__init__(parent)
        self.score_value = 1000
        self.set_home()
        self.npos = Vec(0, 0)

        self.sprite_normal = [TL.load_sprite_animation(get_path("blink_" + i)).set_length(250) for i in Ghost.dir_path]
        
        self.strategy = self.pursue_player
        self.set_sprite(self.sprite_normal[-1])
        
    def get_angle_index(self):
        return int((4 - round(2 * self.vel.angle()/math.pi)) % 4)
        
    def set_sprite_normal(self):
        self.set_sprite(self.sprite_normal[self.get_angle_index()])
        
    def set_sprite_retreat(self):
        self.set_sprite(Ghost.S+prite_Retreat[self.get_angle_index()])
        
    def set_sprite_eaten(self):
        self.set_sprite(Ghost.Sprite_Eyes[self.get_angle_index()])

    def set_home(self, x = 0, y = 0):
        self.home = Vec(x, y)
        return self

    def chase_position(self, matrix):
        ds = (self.pos - self.npos).apply(round).apply(abs)
        if (ds.x < 0.01 or 1 <= ds.x) and (ds.y < 0.01 or 1 <= ds.y):
            i, j = matrix[int(round(self.pos.x))][int(round(self.pos.y))]
            self.npos = Vec(i, j)

        return (self.npos - self.pos).norm()

    def update(self):
        super(Ghost, self).update()
        self.strategy()
        return self

    def pursue_player(self):
        self.set_sprite_normal()
        if (self.pos - self.parent.player.pos).mag_chebyshev() < 1:
            self.parent.player.get_eaten()
        else:
            self.set_vel(self.chase_position(self.parent.player_search_matrix) * 0.05)
        return self

    def retreat_player(self):
        self.set_sprite_retreat()
        if (self.pos - self.parent.player.pos).mag_chebyshev() < 1:
            self.get_eaten()
        else:
            self.set_vel(self.chase_position(self.parent.player_search_matrix_reverse) * 0.03)
        return self

    def pursue_home(self):
        self.set_sprite_eaten()
        if (self.pos - self.home).mag_chebyshev() < 1:
            self.strategy = self.pursue_player
        else:
            self.set_vel(self.chase_position(self.parent.home_search_matrix) * 0.10)
        return self

    def become_edible(self):
        self.strategy = self.retreat_player
        return self
    
    def get_eaten(self):
        self.strategy = self.pursue_home
        
        self.parent.player.score += self.score_value
        if not self.parent.sound_eatghost.isPlaying():
            self.parent.sound_eatghost.play()

class PacManGame(object):
    def get_maze(self):
        return self.maze

    def loadMap(self, path):
        EMPTY = " "
        WALL = "#"
        FOOD = "+"
        POWERPELLET = "-"

        PLAYER = "P"
        GHOST = "G"

        file = open(path, "r")

        self.player = Player(self).set_pos(Vec(1, 1))
        self.ghosts = []
        self.ghost_home = []

        (x, y) = (0, 0)
        arr = []
        for i in file.readlines():
            elem = i.replace("\n", "").split(";")

            x = 0
            row = []
            for j in elem:
                cell = TileUndefined()
                pos = Vec(x, y)

                if j == PLAYER or j == GHOST:
                    if j == PLAYER:
                        self.player.set_pos(pos)
                    if j == GHOST:
                        self.ghosts.append(Ghost(self).set_pos(pos))
                        self.ghost_home.append(pos)
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

        self.maze = Maze().set_buffer(arr)

        n = 100
        k = max(self.maze.get_max_cols(), self.maze.get_max_rows()) + 1
        self.frame = TL.Frame().resize(n * k, n * k).set_tile_scale(n, n).set_pos(Vec(0.5, 0.5))
        self.frame.set_renderer(self.renderer)

        for i in [self.maze] + self.ghosts + [self.player]:
            self.frame.add_child(i)

        self.update_player_search_matrix()
        self.home_search_matrix = search_dijkstra(self.ghost_home, self.maze.get_max_rows(), self.maze.get_max_cols(), self.maze.get_adj_nodes)

    def update_player_search_matrix(self):
        cols, rows = self.maze.get_max_cols(), self.maze.get_max_rows()
        pos = self.player.pos.apply(round).apply(int)

        self.player_search_matrix = search_dijkstra([pos], rows, cols, self.maze.get_adj_nodes)
        self.player_search_matrix_reverse = search_dijkstra_reverse([pos], rows, cols, self.maze.get_adj_nodes)

    def quit_game(self):
        self.stop_all_sounds()

    def load_sounds(self):
        self.sound_intro = self.minim.loadFile("sounds/beginning.wav")
        self.sound_chomp = self.minim.loadFile("sounds/chomp.mp3")
        self.sound_death = self.minim.loadFile("sounds/death.wav")
        self.sound_eatfruit = self.minim.loadFile("sounds/eatfruit.wav")
        self.sound_eatghost = self.minim.loadFile("sounds/eatghost.wav")
        self.sound_extrapac = self.minim.loadFile("sounds/extrapac.wav")
        self.sound_intermission = self.minim.loadFile("sounds/intermission.wav")
        
        self.sound_siren = self.minim.loadFile("sounds/siren.mp3")
        self.sound_siren_retreat = self.minim.loadFile("sounds/siren_retreat.mp3")

    def stop_all_sounds(self):
        self.sound_intro.pause()
        self.sound_chomp.pause()
        self.sound_death.pause()
        self.sound_eatfruit.pause()
        self.sound_extrapac.pause()
        self.sound_intermission.pause()
        self.sound_siren.pause()
        self.sound_siren_retreat.pause()

    def get_score(self):
        return "SCORE - " + str(self.player.score) 

    def get_frame_buffer(self):
        return self.frame.get_frame_buffer()

    def update_cyclegame(self, event):
        self.update_player_search_matrix()

        vel  = Vec(0, 0)            
        pressed = lambda lst: any([event.key_is_pressed(i) for i in lst])
            
        if event.mouse_is_pressed():
            _dir = event.mouse_dir()
            vel = Vec(_dir.x, _dir.y).apply(round)

        if pressed(["a", Ev.Key.LEFT]):
            vel.x = -1
        elif pressed(["d", Ev.Key.RIGHT]):
            vel.x = +1
        if pressed(["w", Ev.Key.UP]):
            vel.y = -1
        elif pressed(["s", Ev.Key.DOWN]):
            vel.y = +1
        
        self.player.set_vel(vel)            

    def updatefn_init(self, event):
        if event.any_key_pressed() or not self.sound_intro.isPlaying():
            self.updatefn = self.updatefn_game
            self.sound_siren.loop()

    def updatefn_game(self, event):
        self.update_cyclegame(event)
        
        self.frame.update()
        self.frame.render()
    
    def __init__(self, minim):
        try:
            self.minim = minim
            self.renderer = TL.SpriteRenderer()
            
            self.loadMap("map1.mz")
            self.load_sounds()
            
            self.frame.render()

            self.updatefn = self.updatefn_game
            self.sound_intro.play()

            self.t = 0

        except Exception as ex:
            util.Error.log("PacManGame Initialization", ex)

    def update(self, event):
        try:
            t = millis()
            if t - self.t > 1:
                self.updatefn(event)
                self.t = t
        except Exception as ex:
            util.Error.log("PacManGame Runtime", ex)
