
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

class Icon(TL.Entity):
    def __init__(self, image):
        super(Icon, self).__init__()
        self.visible = True
        self.set_sprite(image)

    def render(self, buffer, sprite_renderer):
        if self.visible:
            super(Icon, self).render(buffer, sprite_renderer)

class Tile(TL.Entity):
    def __init__(self):
        super(Tile, self).__init__()
        self.score_value = 0
        self.edible = False

    def is_wall(self):
        return False

    def eat(self):
        pass

    def reset(self):
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
        
class TileGhostHome(Tile):
    Sprite = TL.load_sprite(get_path("wall/empty.png"))
    
    def __init__(self):
        super(TileGhostHome, self).__init__()
        self.set_sprite(TileGhostHome.Sprite)

class TileFood(Tile):
    Sprite = TL.load_sprite(get_path("food/food.png"))

    def __init__(self):
        super(TileFood, self).__init__()
        self.reset()

    def eat(self):
        self.set_sprite(TileEmpty.Sprite)
        self.score_value = 0
        self.edible = False

    def reset(self):
        self.set_sprite(TileFood.Sprite)
        self.score_value = 10
        self.edible = True

class TilePowerPellet(TileFood):
    Sprite = TL.load_sprite(get_path("food/powerpellet.png"))

    def __init__(self):
        super(TilePowerPellet, self).__init__()
        self.reset()

    def eat(self):
        self.set_sprite(TileEmpty.Sprite)
        self.score_value = 0
        self.edible = False

    def reset(self):
        self.set_sprite(TilePowerPellet.Sprite)
        self.score_value = 50
        self.edible = True

class TileWall(Tile):
    Sprite = TL.load_sprite(get_path("wall/wall.png"))

    def __init__(self):
        super(TileWall, self).__init__()
        self.set_sprite(TileWall.Sprite)
        
    def is_wall(self):
        return True

class Maze(TL.TileGrid):
    def __init__(self):
        super(Maze, self).__init__()
        self.total_food = 0
        self.eaten_food = 0
    
    def set_buffer(self, arr):
        for i in arr:
            for j in i:
                if isinstance(j, TileFood):
                    self.total_food += 1

        super(Maze, self).set_buffer(arr)
        return self

    def set_tile(self, pos, val):
        if isinstance(val, TileFood):
            self.total_food += 1

    def get_tile(self, pos):
        tile = super(Maze, self).get_tile(pos)
        if tile != None:
            return tile
        else:
            return TileUndefined()

    def is_wall(self, pos):
        tile = super(Maze, self).get_tile(pos)
        if tile != None:
            return tile.is_wall()
        return True

    def reset(self):
        r = self.get_max_cols()
        c = self.get_max_rows()

        for i in range(0, r):
            for j in range(0, c):
                self.get_tile(Vec(i, j)).reset()

        self.eaten_food = 0

    def get_adj_nodes(self, x, y):
        adj_node = []

        for (i, j) in [(-1, 0), (+1, 0), (0, -1), (0, +1)]:
            if not self.is_wall(Vec(x + i, y + j)):
                adj_node.append((x + i, y + j))

        return adj_node

    def eat_tile(self, player, soundeffect, powerup):
        pos = player.pos.apply(round)
        tile = self.get_tile(pos)
        
        if tile.edible:
            player.score += tile.score_value
            self.eaten_food += 1

            if not soundeffect.isPlaying():
                soundeffect.rewind()
                soundeffect.play()

            if isinstance(tile, TilePowerPellet):
                powerup()

            self.get_tile(pos).eat()
                
    def is_cleared(self):
        return (self.eaten_food == self.total_food)

class Mover(TL.Entity):
    def __init__(self, parent):
        super(Mover, self).__init__()
        self.parent = parent

        self.ppos = Vec(0, 0)
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

        self.ppos = self.pos

class Player(Mover):
    def __init__(self, parent):
        super(Player, self).__init__(parent)
        self.score = 0
        self.move_animation = TL.load_sprite_animation(get_path("player")).set_length(250)
        self.death_animation = TL.load_sprite_animation(get_path("player_death")).set_length(500)
        self.death_animation.loop = False

        self.reset()

    def set_pos(self, pos = Vec(0, 0)):
        super(Player, self).set_pos(pos)
        self.initial_pos = pos
        return self

    def reset(self):
        self.pos = self.initial_pos
        self.t = 0
        self.set_sprite(self.move_animation)
        return self

    def set_vel(self, vel):
        if vel.mag_manhattan() != 0:
            super(Player, self).set_vel(vel.norm() * 0.10)
        return self

    def update(self):
        super(Player, self).update()
        self.set_angle(self.vel.angle())
        return self

    def get_eaten(self):
        if not self.parent.konami:
            self.parent.stop_all_sounds()
            self.parent.sound_death.play()

            self.death_animation.reset()
            self.set_sprite(self.death_animation)
            self.parent.player_death()
        return self

class Ghost(Mover):
    dir_path = ["right", "up", "left", "down"]
    Sprite_Eyes = [TL.load_sprite(get_path("eyes/eyes_" + i + ".png")) for i in dir_path]
    Sprite_Edible = [TL.load_sprite_animation(get_path("chase_" + i)).set_length(500) for i in dir_path]

    CHASE = 0
    EDIBLE = 1
    EATEN = 2

    def __init__(self, parent):
        super(Ghost, self).__init__(parent)
        self.mid = 350
        self.len_interv = 400

        self.chase_vel = 0.07
        self.fright_vel = 0.04
        self.scatter_vel = 0.04
        self.home_vel = 0.30

        self.score_value = 1000
        self.t = 0

        if not hasattr(self, 'sprite_normal'):
            k = ["blink", "ink", "clyde", "shadow"][random.randint(0, 3)] + "_"
            self.sprite_normal = [TL.load_sprite_animation(get_path(k + i)).set_length(250) for i in Ghost.dir_path]
        
        self.reset()

    def reset(self):
        self.pos = self.initial_pos
        self.set_sprite(self.sprite_normal[-1])
        self.state = Ghost.CHASE
        self._next_pos = Vec(0, 0)
        self.t = 0

        return self

    def set_pos(self, pos = Vec(0, 0)):
        super(Ghost, self).set_pos(pos)
        self.initial_pos = pos
        return self

    def get_angle_index(self):
        return int(abs(4 - round(2 * self.vel.angle()/math.pi))) % 4

    def get_direction(self, search_matrix):
        ds = (self.pos - self._next_pos).apply(round).apply(abs)
        
        if (ds.x < 0.01 or 1 <= ds.x) and (ds.y < 0.01 or 1 <= ds.y):
            i, j = self.pos.apply(round).apply(int)
            pos_lst = search_matrix[i][j]
            
            if pos_lst != [] and pos_lst != None:
                if isinstance(pos_lst, list):
                    i, j = pos_lst[0]
                else:
                    i, j = pos_lst
                
                self._next_pos = Vec(i, j)
            else:
                self._next_pos = self.pos

        return (self._next_pos - self.pos).norm()
        
    def chase(self):
        self.set_sprite(self.sprite_normal[self.get_angle_index()])

        interv = self.t % self.len_interv
        if interv < self.mid:
            vel = self.get_direction(self.parent.player_search_matrix) * self.chase_vel
        elif interv >= self.mid:
            if interv == self.mid:
                maze = self.parent.get_maze()
                r, c = maze.get_max_cols(), maze.get_max_rows()

                p = Vec(0, 0)
                while maze.get_tile(p).is_wall() and (self.pos - p).mag_manhattan > 5:
                    p = Vec(random.randint(0, r - 1), random.randint(0, c - 1))

                self.search_matrix = search_dijkstra([p], c, r, maze.get_adj_nodes)
        
            vel = self.get_direction(self.search_matrix) * self.scatter_vel
        
        self.set_vel(vel)

    def update(self):
        super(Ghost, self).update()
    
        if self.state == Ghost.CHASE:
            self.set_sprite(self.sprite_normal[self.get_angle_index()])

            interv = self.t % self.len_interv
            if interv < self.mid:
                self.set_vel(self.get_direction(self.parent.player_search_matrix) * self.chase_vel)
            elif interv >= self.mid:
                if interv == self.mid:
                    maze = self.parent.get_maze()
                    r, c = maze.get_max_cols(), maze.get_max_rows()
                    p = Vec(0, 0)

                    while maze.get_tile(p).is_wall() and (self.pos - p).mag_manhattan > 5:
                        p = Vec(random.randint(0, r - 1), random.randint(0, c - 1))

                    self.search_matrix = search_dijkstra([p], c, r, maze.get_adj_nodes)
            
                self.set_vel(self.get_direction(self.search_matrix) * self.scatter_vel)
            
        elif self.state == Ghost.EDIBLE:
            self.set_sprite(Ghost.Sprite_Edible[self.get_angle_index()])
            self.set_vel(self.get_direction(self.parent.player_search_matrix_reverse) * self.fright_vel)
        elif self.state == Ghost.EATEN:
            self.set_sprite(Ghost.Sprite_Eyes[self.get_angle_index()])
            self.set_vel(self.get_direction(self.parent.home_search_matrix) * self.home_vel)
            
            if isinstance(self.parent.get_maze().get_tile(self.pos.apply(round)), TileGhostHome):
                self.state = Ghost.CHASE
            
        self.t += 1

    def get_eaten(self, player):
        if (self.pos - self.parent.player.pos).mag_chebyshev() < 1:
            if self.state == Ghost.CHASE:
                player.get_eaten()
            elif self.state == Ghost.EDIBLE:
                self.state = Ghost.EATEN

                if not self.parent.sound_eatghost.isPlaying():
                    self.parent.sound_eatghost.rewind()
                    self.parent.sound_eatghost.play()
                return 1000
        return 0

    def become_edible(self):
        if self.state == Ghost.CHASE:
            self.state = Ghost.EDIBLE
        return self

    def become_inedible(self):
        if self.state == Ghost.EDIBLE:
            self.state = Ghost.CHASE
        return self

class Blink(Ghost):
    def __init__(self, parent):
        self.sprite_normal = [TL.load_sprite_animation(get_path("blink_" + i)).set_length(250) for i in Ghost.dir_path]
        super(Blink, self).__init__(parent)

        self.mid = 350
        self.len_interv = 400

        self.chase_vel = 0.07
        self.fright_vel = 0.04
        self.scatter_vel = 0.04
        self.home_vel = 0.30

class Clyde(Ghost):
    def __init__(self, parent):
        self.sprite_normal = [TL.load_sprite_animation(get_path("clyde_" + i)).set_length(250) for i in Ghost.dir_path]
        super(Clyde, self).__init__(parent)

        self.mid = 100
        self.len_interv = 400

        self.chase_vel = 0.02
        self.fright_vel = 0.03
        self.scatter_vel = 0.02
        self.home_vel = 0.30


class Ink(Ghost):
    def __init__(self, parent):
        self.sprite_normal = [TL.load_sprite_animation(get_path("ink_" + i)).set_length(250) for i in Ghost.dir_path]
        super(Ink, self).__init__(parent)

        self.mid = 200
        self.len_interv = 400

        self.chase_vel = 0.05
        self.fright_vel = 0.04
        self.scatter_vel = 0.03
        self.home_vel = 0.30

class Shadow(Ghost):
    def __init__(self, parent):
        self.sprite_normal = [TL.load_sprite_animation(get_path("shadow_" + i)).set_length(250) for i in Ghost.dir_path]
        super(Shadow, self).__init__(parent)

        self.mid = 250
        self.len_interv = 400

        self.chase_vel = 0.04
        self.fright_vel = 0.03
        self.scatter_vel = 0.02
        self.home_vel = 0.30

class PacManGame(object):
    def loadMap(self, path):
        file = open(path, "r")

        self.player = Player(self).set_pos(Vec(1, 1))
        self.ghosts = []
        self.ghost_home = []
        self.num_pellets = 0

        (x, y) = (0, 0)
        arr = []
        for i in file.readlines():
            elem = i.replace("\n", "").split(";")

            x = 0
            row = []
            for j in elem:
                cell = TileUndefined()
                pos = Vec(x, y)

                if j == "P":
                    self.player.set_pos(pos)
                    cell = TileEmpty()
                elif any((j == x for x in ["B", "C", "I", "S", "G"])):
                    fn = Ghost
                    if j == "B":
                        fn = Blink
                    elif j == "C":
                        fn = Clyde
                    elif j == "I":
                        fn = Ink
                    elif j == "S":
                        fn = Shadow
                    
                    self.ghosts.append(fn(self).set_pos(pos))
                    self.ghost_home.append(pos)
                    cell = TileGhostHome()
                elif j == " ":
                    cell = TileEmpty()
                elif j == "#":
                    cell = TileWall()
                elif j == "+":
                    cell = TileFood()
                    self.num_pellets += 1
                elif j == "-":
                    cell = TilePowerPellet()
                    self.num_pellets += 1

                row.append(cell)

                x += 1
            arr.append(row)
            y += 1

        file.close()

        self.maze = Maze().set_buffer(arr)

        n = 100
        c, r = self.maze.get_max_cols(), self.maze.get_max_rows() + 1
        k = max(c, r) + 1
        self.frame = TL.Frame().resize(n * k, n * k).set_tile_scale(n, n).set_pos(Vec(0.5, 0.5))
        self.frame.set_renderer(self.renderer)


        self.icons_lives = []

        x = 0
        for i in ["player/0.png"] * 3:
            self.icons_lives.append(Icon(TL.load_sprite(get_path(i))).set_pos(Vec(x, r - 1))) 
            x += 1


        for i in [self.maze] + self.ghosts + [self.player] + self.icons_lives:
            self.frame.add_child(i)

        self.update_player_search_matrix()
        self.home_search_matrix = search_dijkstra(self.ghost_home, self.maze.get_max_rows(), self.maze.get_max_cols(), self.maze.get_adj_nodes)

    def update_player_search_matrix(self):
        cols, rows = self.maze.get_max_cols(), self.maze.get_max_rows()
        pos = self.player.pos.apply(round).apply(int)

        self.player_search_matrix = search_dijkstra([pos], rows, cols, self.maze.get_adj_nodes)
        self.player_search_matrix_reverse = search_dijkstra_reverse([pos], rows, cols, self.maze.get_adj_nodes)

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

    def quit_game(self):
        self.stop_all_sounds()
    
    def get_maze(self): 
        return self.maze

    def get_score(self):
        return self.msg

    def get_frame_buffer(self):
        return self.frame.get_frame_buffer()

    def play_intro(self):
        self.frame.render()

        self.t = 0
        self.power_up_timer = 0

        self.sound_intro.rewind()
        self.sound_intro.play()

        def update(event):
            if event.any_key_pressed() or not self.sound_intro.isPlaying():
                self.msg = "PACMAN"
                self.updatefn = self.game_loop
                self.sound_siren.loop()
        
        self.updatefn = update

    def reset_game(self):
        self.player.score = 0
        self.level = 0
        self.lives = 3
        self.msg = "PACMAN"
        
        self.konami = False
        self.konami_stack = 0

        self.stack = []

        self.player.reset()
        for i in self.ghosts:
            i.reset()

    def load_game(self):
        self.loadMap("map1.mz")
        self.reset_game()
        self.play_intro()

    def next_level(self):
        self.level += 1
        self.msg = "NEXT LEVEL {0}".format(self.level)
        self.maze.reset()

        self.player.reset()
        for i in self.ghosts:
            i.reset()

        t = util.get_millis()
        def wait(event):
            if util.get_millis() - t > 2000:
                self.play_intro()

        self.updatefn = wait

    def player_death(self):
        self.lives -= 1

        if self.lives == 0:
            self.msg = "GAME OVER!"

            t = util.get_millis()
            def ending(event):
                self.frame.render()

                if util.get_millis() - t > 2000:
                    self.reset_game()
                    self.play_intro()

            self.updatefn = ending
        else:
            t = util.get_millis()
            def continue_game(event):
                self.frame.render()

                if util.get_millis() - t > 2000:
                    self.player.reset()
                    for i in self.ghosts:
                        i.reset()

                    self.play_intro()

            self.msg = "{0} LIVES LEFT".format(self.lives)
            self.updatefn = continue_game

    def game_loop(self, event):
        px, py = self.player.pos.apply(round)
        
        self.msg = "SCORE:{1} FPS:{2:2.2f} LVL:{4} LIFE:{5}".format(self.maze.eaten_food,
                 self.player.score, util.get_framerate(), self.power_up_timer, self.level, self.lives)
        self.player_update(self.player, event)
        self.player_eat_tile(self.player)
        self.frame.update()
        self.frame.render()
        
        Px, Py = self.player.pos.apply(round)
        if px != Px or py != Py:
            self.update_player_search_matrix()

        if self.maze.is_cleared():
            self.next_level()

    def player_eat_tile(self, player):
        def powerup():
            self.power_up_timer = 300

            for i in self.ghosts:
                i.become_edible()

        self.maze.eat_tile(player, self.sound_chomp, powerup)

        score = 0
        for i in self.ghosts:
            score += i.get_eaten(player)
        
        player.score += score

        if self.power_up_timer > 1: 
            self.power_up_timer -= 1
        elif self.power_up_timer == 1:
            for i in self.ghosts:
                i.become_inedible()

            self.power_up_timer = 0

    def player_update(self, player, event):
        vel = Vec(0, 0)            
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
            
        player.set_vel(vel)    

    def __init__(self, minim):
        try:    
            self.minim = minim
            self.renderer = TL.SpriteRenderer()

            self.load_sounds()
            self.load_game()
        except Exception as ex:
            util.Error.log("PacMan Initialization", ex)

    def konami_code(self, event):
        def next(num, key):
            if self.konami_stack == num and event.key_is_pressed(key):
                self.konami_stack += 1
                return True

            return False

        lst = [Ev.Key.LEFT, Ev.Key.LEFT, Ev.Key.RIGHT, Ev.Key.RIGHT] + [Ev.Key.UP, Ev.Key.DOWN] * 2 + ["a", "b"]
        for i in range(0, len(lst)):
            if next(i, lst[i]):
                break

        if self.konami_stack == len(lst):
            self.konami_stack = 0
            self.konami = not self.konami

    def update_icons(self):
        for i in range(0, self.lives):
            self.icons_lives[i].visible = True
        for i in range(self.lives, 3):
            self.icons_lives[i].visible = False

    def update(self, event):
        try:
            t = util.get_millis()
            if t - self.t > 1:
                self.konami_code(event)
                self.update_icons()

                self.updatefn(event)
                self.t = t
                
                if self.konami:
                    self.msg = "KONAMI!"
        except Exception as ex:
            util.Error.log("PacMan Runtime", ex)
