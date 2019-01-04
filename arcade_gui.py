import user_interface as UI
import game_pacman as PAC
import arcade as STYLE

import events as EVENTS
import os
import copy
import random

class UI_MainMenu(STYLE.UI_State):
    def __init__(self, parent):
        super(UI_MainMenu, self).__init__(parent)
        
        title = "PyRAE"
        logo = STYLE.create_label(0.2, 0.1, 0.8, 0.4, title)
        logo.frame = UI.NoneWidget()

        subtitle = STYLE.create_label(0.2, 0.35, 0.8, 0.45, "Python RETRO ARCADE EMULATOR")
        subtitle.frame = UI.NoneWidget()

        self.center_frame.add_widget(logo).add_widget(subtitle)

        y = 0.5
        dy = 0.08
        padding = 0.02
        for i, j in [("Play", UI_Play), ("Options", UI_Options), ("Quit", UI_Exit)]:
            self.center_frame.add_widget(STYLE.create_button(0.2, y, 0.8, y + dy, i, self.parent.create_state_changer(j)))
            y += dy + padding

        credit = STYLE.create_label(0.5, 0.9, 1, 0.95, "Created By Sigmaphi")
        credit.frame = UI.NoneWidget()

        self.right_frame.add_widget(credit)

        def fn_update(event):
            if random.randint(0, 10) < 2:
                L0 = 0
                L1 = 255
                txt = ""
                for i in title:
                    if random.randint(0, 10) < 2:
                        txt += chr(random.randint(L0, L1))
                    else:
                        txt += i

                logo.caption.set_text(txt)

        self.update_func = fn_update

class UI_Play(STYLE.UI_State):
    def __init__(self, parent):
        super(UI_Play, self).__init__(parent)

        x1, x2 = 0.2, 0.8
        y = 0.2
        dy = 0.08
        padding = 0.02

        for (i, j) in [("PacMan", UI_PlayPacMan)]:
            self.center_frame.add_widget(STYLE.create_button(x1, y, x2, y + dy, i, self.parent.create_state_changer(j)))
            y += dy + padding

        for i in []:
            self.center_frame.add_widget(STYLE.create_label(x1, y, x2, y + dy, i))
            y += dy + padding

        self.center_frame.add_widget(STYLE.create_button(x1, y, x2, y + dy, "BACK", self.parent.create_state_changer(UI_MainMenu)))

class UI_PlayPacMan(STYLE.UI_State):
    def __init__(self, parent):
        super(UI_PlayPacMan, self).__init__(parent)
        
        game = PAC.PacManGame(self.parent.minim)
        game_window = UI.FrameBuffer().set_corners(0.05, 0.05, 0.95, 0.95).set_shader(self.parent.shader_manager.get_game_shader())

        score = STYLE.create_label(0, 0, 1, 0.05, "")

        def quit_game():
            game.quit_game()
            self.parent.change_state(UI_Play)
            self.parent.highscores.add_new_score("Player", game.get_score())
        
        def _update(event):
            game.update(event)
            game_window.set_buffer(game.get_frame_buffer())
            score.caption.set_text(game.get_score())

        self.update_func = _update
        self.center_frame.add_widget(game_window).add_widget(score).add_widget(STYLE.create_label(0.8, 0, 1, 0.05, ""))
        self.left_frame.add_widget(STYLE.create_button(0, 0, 0.2, 0.05, "Menu", quit_game))

class Highscores(object):
    def __init__(self):
        self.scores = []

    def get_scores(self):
        scores = []
        for i in range(0, 5):
            if i >= len(self.scores):
                scores.append(" - : 0")
            else:
                n, s = self.scores[i]
                scores.append(str(n) + " : " + str(s))
        return scores
    
    def add_new_score(self, name, score):
        self.scores.append((name, score))
        self.scores.sort()

class UI_Highscores(STYLE.UI_State):
    def __init__(self, parent):
        super(UI_Highscores, self).__init__(parent)
        scores = self.parent.highscores.get_scores()

        padding = 0.02
        dy = 0.1
        y = 0.1
        for i in scores:
            self.center_frame.add_widget(STYLE.create_label(0.2, y, 0.8, y + dy, i))
            y += dy + padding

        self.center_frame.add_widget(STYLE.create_button(0.2, y, 0.8, y + dy, "Main Menu", self.parent.create_state_changer(UI_MainMenu)))

class UI_Options(STYLE.UI_State):
    def __init__(self, parent):
        super(UI_Options, self).__init__(parent)
        
        ui_shader_button   = STYLE.create_button(0.1, 0.3, 0.9, 0.38)
        game_shader_button = STYLE.create_button(0.1, 0.4, 0.9, 0.48)

        def set_ui_caption():
            ui_shader_button.caption.set_text(self.parent.shader_manager.get_ui_shader_name())
        
        def set_game_caption():
            game_shader_button.caption.set_text(self.parent.shader_manager.get_game_shader_name())
        
        def change_ui_shader():
            self.parent.shader_manager.next_ui_shader()
            set_ui_caption()
            
        def change_game_shader():
            self.parent.shader_manager.next_game_shader()
            set_game_caption()

        set_ui_caption()
        set_game_caption()
        STYLE.set_callback(ui_shader_button, change_ui_shader)
        STYLE.set_callback(game_shader_button, change_game_shader)

        back_button = STYLE.create_button(0.1, 0.5, 0.9, 0.58, "Back", self.parent.create_state_changer(UI_MainMenu))

        self.center_frame.add_widget_list([ui_shader_button, game_shader_button, back_button])

class UI_Exit(STYLE.UI_State):
    def __init__(self, parent):
        super(UI_Exit, self).__init__(parent)
        self.center_frame.add_widget(STYLE.create_label(0.2, 0.5, 0.8, 0.58, "Are you sure you want to quit ?").caption.set_size(40))
        self.center_frame.add_widget(STYLE.create_button(0.2, 0.6, 0.48, 0.68, "Quit", exit))
        self.center_frame.add_widget(STYLE.create_button(0.52, 0.6, 0.8, 0.68, "Cancel", self.parent.create_state_changer(UI_MainMenu)))

class ShaderManager(object):
    def __init__(self):
        self.ui_shaders = []
        self.game_shaders = []

        self.load_shaders()
        self.current_ui_shader = 0
        self.current_game_shader = 0 

    def load_shaders(self):
        def get_shaders_dir(path):
            shaders_path = filter(lambda x: os.path.isfile(os.path.join(path, x)), os.listdir(path))
            shaders_abs_path = map(lambda x: os.path.join(path, x), shaders_path)
            return shaders_abs_path

        def map_shader(name):
            return lambda i: (loadShader(i), name + " - " + os.path.splitext(os.path.basename(i))[0])
        
        _path = sketchPath()
        
        self.ui_shaders = map(map_shader("UI Shader"), get_shaders_dir(os.path.join(_path, "shaders", "ui")) + get_shaders_dir(os.path.join(_path, "shaders")))
        self.game_shaders = map(map_shader("Game Shader"), get_shaders_dir(os.path.join(_path, "shaders", "game")) + get_shaders_dir(os.path.join(_path, "shaders")))
        
        return self
    
    def next_ui_shader(self):
        self.current_ui_shader += 1
        if self.current_ui_shader >= len(self.ui_shaders):
            self.current_ui_shader = 0
        return self

    def next_game_shader(self):
        self.current_game_shader += 1
        if self.current_game_shader >= len(self.game_shaders):
            self.current_game_shader = 0
        return self

    def get_ui_shader(self):
        (_shader, _) = self.ui_shaders[self.current_ui_shader]
        return _shader

    def get_ui_shader_name(self):
        (_, name) = self.ui_shaders[self.current_ui_shader]
        return name

    def get_game_shader(self):
        (_shader, _) = self.game_shaders[self.current_game_shader]
        return _shader

    def get_game_shader_name(self):
        (_, name) = self.game_shaders[self.current_game_shader]
        return name

class Arcade(object):
    def change_state(self, state_constructor):
        self.previous_state = self.current_state
        self.current_state = state_constructor(self)

    def create_state_changer(self, state_constructor):
        def change_state():
            self.change_state(state_constructor)
        
        return change_state

    def set_undo_state(self):
        self.current_state = self.previous_state

    def __init__(self, minim, keyboard, mouse):
        self.shader_manager = ShaderManager()
        self.game_shader = self.shader_manager.get_game_shader()
        self.highscores = Highscores()

        self.window = UI.Window().set_shader(self.shader_manager.get_ui_shader())

        import events as EVENTS
        import arcade_gui as AG

        self.event = EVENTS.Event(keyboard, mouse)
        self.current_state = AG.UI_MainMenu(self)
        self.stop_loop = False

        self.minim = minim
        self.input = self.minim.getLineIn()

    def update(self):
        if not self.stop_loop:
            try:
                self.window.set_shader(self.shader_manager.get_ui_shader())
                self.current_state.update(self.event)
            except Exception as ex:
                print("Runtime Error : " + repr(ex))
                self.stop_loop = True

    def resize(self, w, h):
        self.window.set_corners(0, 0, w, h)
        self.window.resize_buffer(w, h)
