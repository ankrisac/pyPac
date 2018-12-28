import time
import tile_map as TL
import events as Ev
import copy
import random
import math

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

class Mover(TL.Entity):
    def __init__(self, parent):
        super(Mover, self).__init__()
        self.parent = parent

        self.pos_x, self.pos_y = (0, 0)
        self.vel_x, self.vel_y = (0, 0)
        self.pvel_x, self.pvel_y = (0, 0)
        
    def set_vel(self, x, y):
        (self.pvel_x, self.pvel_y) = (self.vel_x, self.vel_y)
        (self.vel_x, self.vel_y) = (x, y)
        
    def update(self):
        get_tile = lambda x, y: self.parent.maze.get_tile(int(x), int(y))
        is_wall = lambda x, y: get_tile(x, y).is_wall() if get_tile(x, y) != None else True
        
        r = 0.1
        def collide(x, y):
            (x1, y1) = (math.floor(x + r), math.floor(y + r))
            (x2, y2) = (math.ceil(x - r), math.ceil(y - r))
            return (is_wall(x1, y1) or is_wall(x1, y2) or is_wall(x2, y1) or is_wall(x2, y2))
            
        def try_to_move(vx, vy):
            (x, y) = (self.pos_x, self.pos_y)
            (px, py) = (x + vx, y + vy)

            if not collide(px, py):
                (self.pos_x, self.pos_y) = (px, py)
            elif not collide(px, y):
                (self.pos_x, self.pos_y) = (px, y)
            elif not collide(x, y):
                (self.pos_x, self.pos_y) = (x, py)
            else:
                return True
            return False

        if not try_to_move(self.vel_x, self.vel_y):
            try_to_move(self.pvel_x, self.pvel_y)

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

    def input_motion(self, x, y):
        self.set_vel(x * self.player_vel, y * self.player_vel)

    def updatefn_move(self):
        super(Player, self).update()
        self.set_angle(math.pi/2 - math.atan2(self.vel_x, self.vel_y))

        cell = self.parent.maze.get_tile(round(self.pos_x), round(self.pos_y))

        if isinstance(cell, TileFood):
            self.score += cell.score_value
            
            self.parent.maze.set_tile(round(self.pos_x), round(self.pos_y), TileEmpty())
            
            if isinstance(cell, TilePowerPellet):
                self.parent.power_up()
                
            if not self.parent.sound_chomp.isPlaying():
                self.parent.sound_chomp.loop(1)
            cell.eat()

    def get_eaten(self):
        self.set_angle(0)
        self.parent.stop_all_sounds()
        self.parent.sound_death.play()

        self.update = lambda: None
        self.death_animation.reset()
        self.set_sprite(self.death_animation)
        self.get_eaten = lambda: None

def search_dijkstra(search_matrix, max_rows, max_cols, get_adj_node):
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

    iter_set = copy.copy(search_matrix)
    for (i, j) in search_matrix:
        path_matrix[i][j]

    while iter_set != []:
        iter_set = iterate_search(iter_set)

    return path_matrix

def search_dijkstra_reverse(search_matrix, max_rows, max_cols, get_adj_node):
    path_matrix = [[None for i in range(0, max_cols)] for j in range(0, max_rows)]
    
    def iterate_search(iter_set):
        next_cells = []
    
        for (i, j) in iter_set:
            adj_cell = get_adj_node(i, j)
            
            path_matrix[i][j] = []
            for (m, n) in adj_cell:
                if path_matrix[m][n] is None:
                    path_matrix[i][j].append((m, n))
                    next_cells.append((m, n))
    
        return list(set(next_cells))

    iter_set = copy.copy(search_matrix)
    for (i, j) in search_matrix:
        path_matrix[i][j]

    while iter_set != []:
        iter_set = iterate_search(iter_set)

    return path_matrix

class Ghost(Mover):
    Sprite_Eyes = None
    Sprite_Retreat = None
    
    def __init__(self, parent):
        super(Ghost, self).__init__(parent)
        self.score_value = 1000
        self.ghost_vel = 0.05
        self.set_home()
        
        (self.next_x, self.next_y) = (0, 0)

        
        t1 = 250
        dir_path = ["right", "up", "left", "down"]
        self.sprite_normal = [TL.load_sprite_animation(get_path("blink_" + i)).set_length(t1) for i in dir_path]
        
        if Ghost.Sprite_Retreat == None:
            t2 = 500
            Ghost.Sprite_Retreat = [TL.load_sprite_animation(get_path("chase_" + i)).set_length(t2) for i in dir_path]
        if Ghost.Sprite_Eyes == None:
            Ghost.Sprite_Eyes = [TL.load_sprite(get_path("eyes/eyes_" + i + ".png")) for i in dir_path]

        self.strategy = self.pursue_player
        self.set_sprite(self.sprite_normal[-1])
        
    def get_angle_index(self):
        theta = round(2 * math.atan2(self.vel_x, self.vel_y)/math.pi)
        
        if theta == 0:
            return 3
        elif theta == 1:
            return 0
        elif theta == -1:
            return 2
        elif theta == 2:
            return 1
        elif theta == -2:
            return 1
        return 0
        
    def set_sprite_normal(self):
        self.set_sprite(self.sprite_normal[self.get_angle_index()])
        
    def set_sprite_retreat(self):
        self.set_sprite(Ghost.Sprite_Retreat[self.get_angle_index()])
        
    def set_sprite_eaten(self):
        self.set_sprite(Ghost.Sprite_Eyes[self.get_angle_index()])

    def set_home(self, x = 0, y = 0):
        self.home_x, self.home_y = (x, y)
        return self

    def _get_adj_nodes(self, i, j):
        adj_node = []

        for (di, dj) in [(-1, 0), (+1, 0), (0, -1), (0, +1)]:
            (I, J) = (i + di, j + dj)

            tile = self.parent.get_maze().get_tile(I, J)
            if tile != None and not tile.is_wall():
                adj_node.append((I, J))

        return adj_node

    def find_shortest_path(self, lst):
        (c, r) = (self.parent.maze.get_max_cols(), self.parent.maze.get_max_rows())   
        path_matrix = search_dijkstra(lst, c, r, self._get_adj_nodes)

        (dx, dy) = (abs(round(self.pos_x) - self.next_x), abs(round(self.pos_y) - self.next_y))
        if (dx < 0.01 or 1 <= dx) and (dy < 0.01 or 1 <= dy):
            (self.next_x, self.next_y) = path_matrix[int(round(self.pos_x))][int(round(self.pos_y))]
                    
        (Dx, Dy) = (self.next_x - self.pos_x, self.next_y - self.pos_y)

        D = math.sqrt(Dx*Dx + Dy*Dy)
        return (Dx / D * self.ghost_vel, Dy / D * self.ghost_vel)

    def find_shortest_path_reverse(self, lst):
        (c, r) = (self.parent.maze.get_max_cols(), self.parent.maze.get_max_rows())   
        path_matrix = search_dijkstra_reverse(lst, c, r, self._get_adj_nodes)
    
        (dx, dy) = (abs(round(self.pos_x) - self.next_x), abs(round(self.pos_y) - self.next_y))
        if (dx < 0.01 or 1 <= dx) and (dy < 0.01 or 1 <= dy):
            path = path_matrix[int(round(self.pos_x))][int(round(self.pos_y))]
            
            if path != []:
                (self.next_x, self.next_y) = path[0]
                    
        (Dx, Dy) = (self.next_x - self.pos_x, self.next_y - self.pos_y)
    
        D = math.sqrt(Dx*Dx + Dy*Dy)
        return (Dx / D * self.ghost_vel, Dy / D * self.ghost_vel)


    def update(self):
        super(Ghost, self).update()
        self.strategy()
        return self

    def pursue_player(self):
        self.set_sprite_normal()
        if abs(self.pos_x - self.parent.player.pos_x) < 1 and abs(self.pos_y - self.parent.player.pos_y) < 1:
            self.parent.player.get_eaten()
        else:
            self.ghost_vel = 0.05
            vx, vy = self.find_shortest_path([(int(round(self.parent.player.pos_x)), int(round(self.parent.player.pos_y)))])
            self.set_vel(vx, vy)
        return self

    def retreat_player(self):
        self.set_sprite_retreat()
        if abs(self.pos_x - self.parent.player.pos_x) < 1 and abs(self.pos_y - self.parent.player.pos_y) < 1:
            self.get_eaten()
        else:
            self.ghost_vel = 0.03
            vx, vy = self.find_shortest_path_reverse([(int(round(self.parent.player.pos_x)), int(round(self.parent.player.pos_y)))])
            self.set_vel(vx, vy)
        return self

    def pursue_home(self):
        self.set_sprite_eaten()
        if abs(self.pos_x - self.home_x) < 1 and abs(self.pos_y - self.home_y) < 1:
            self.strategy = self.pursue_player
        else:
            self.ghost_vel = 0.10
            vx, vy = self.find_shortest_path([(self.home_x, self.home_y)])
            self.set_vel(vx, vy)
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

        self.player = Player(self).set_pos(1, 1)
        self.ghosts = []

        (x, y) = (0, 0)
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
                        self.ghosts.append(Ghost(self).set_pos(x, y).set_home(x, y))
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
        return "SCORE - " # + str(self.player.score) 

    def player_move(self, event):
        x, y  = (0, 0)
            
        pressed = lambda lst: any([event.key_is_pressed(i) for i in lst])
            
        if event.mouse_is_pressed():
            _dir = event.mouse_dir()
            _dir.normalize()
            x, y = round(_dir.x), round(_dir.y)

        if pressed(["a", Ev.Key.LEFT]):
            x = -1
        elif pressed(["d", Ev.Key.RIGHT]):
            x = +1
        if pressed(["w", Ev.Key.UP]):
            y = -1
        elif pressed(["s", Ev.Key.DOWN]):
            y = +1

        if (x, y) != (0, 0):
            (x, y) = (x / math.sqrt(2), y / math.sqrt(2))
        if x != 0 or y != 0:
            self.player.input_motion(x, y)                

    def updatefn_init(self, event):
        if event.any_key_pressed() or not self.sound_intro.isPlaying():
            self.update = self.updatefn_game
            self.sound_siren.loop()

    def updatefn_game(self, event):
        self.player_move(event)
        
        self.frame.update()
        self.frame.render()

    def get_frame_buffer(self):
        return self.frame.get_frame_buffer()
    
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
            print("PacManGame Initialization : ", ex)

    def update(self, event):
        try:
            t = millis()
            if t - self.t > 10:
                self.updatefn(event)
        except Exception as ex:
            print("PacManGame Runtime : ", ex)
