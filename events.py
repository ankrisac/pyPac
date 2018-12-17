class Key(object):
    BEGIN = 0
    BACKSPACE = BEGIN

    ENTER = BACKSPACE + 1
    ESCAPE = ENTER + 1
    DELETE = ENTER + 2

    UP    = DELETE + 1
    DOWN  = UP + 1
    LEFT  = UP + 2
    RIGHT = UP + 3

    TAB   = RIGHT + 1
    SHIFT = TAB + 1
    CTRL  = TAB + 2
    ALT   = TAB + 3

    END = ALT + 1

def isKey(key):
    return isinstance(i, str) and len(i) == 1

def isSpecialKey(key):
    return Key.BEGIN <= key < Key.END and isinstance(key, int)

def key_to_str(i):
    if isSpecialKey(i):
        return "SPECIAL KEY"
    elif isKey(i):
        return i
    else:
        return "ERROR"

class keyData(object):
    def __init__(self):
        self.key_val = [False for x in range(0, 256)]
        self.special_key = [False for x in range(0, Key.END)]

    def set_key(self, key_val, key_code, val):
        if key_val != CODED:
            if key_val == ESC:
                self.special_key[Key.ESCAPE] = val
            elif key_val == TAB:
                self.special_key[Key.TAB] = val
            elif key_val == DELETE:
                self.special_key[Key.DELETE] = val
            elif key_val == BACKSPACE:
                self.special_key[Key.BACKSPACE] = val
            elif key_val == ENTER or key_val == RETURN:
                self.special_key[Key.ENTER] = val
            self.key_val[ord(key_val)] = val
        elif key_code == UP:
            self.special_key[Key.UP] = val
        elif key_code == DOWN:
            self.special_key[Key.DOWN] = val
        elif key_code == LEFT:
            self.special_key[Key.LEFT] = val
        elif key_code == RIGHT:
            self.special_key[Key.RIGHT] = val
        elif key_code == ALT:
            self.special_key[Key.ALT] = val
        elif key_code == CONTROL:
            self.special_key[Key.CTRL] = val
        elif key_code == SHIFT:
            self.special_key[Key.SHIFT] = val

    def is_pressed(self, val):
        if isinstance(val, int) and val < len(self.special_key):
            return self.special_key[val]
        elif isinstance(val, str) and len(val) == 1:
            return self.key_val[ord(val)]

    def any_key_pressed(self):
        for i in self.key_val + self.special_key:
            if i == True:
                return True
        return False

class KeyBoard_Event(object):
    def __init__(self):
        self.key_data = keyData()

    def press(self):
        self.key_data.set_key(this.key, this.keyCode, True)

    def release(self):
        self.key_data.set_key(this.key, this.keyCode, False)

    def is_pressed(self, i):
        return self.key_data.is_pressed(i)

class Mouse_Event(object):
    def __init__(self):
        self.mouse_pos = PVector(0, 0)
        self.mouse_pressed = False

    def press(self):
        self.mouse_pressed = True

    def release(self):
        self.mouse_pressed = False

    def move(self):
        self.mouse_pos = PVector(mouseX, mouseY)

class Event(object):
    def __init__(self, keyboard, mouse):
        self._keyboard = keyboard
        self._mouse = mouse

        self._key_val = []
        self._mouse_pos = PVector(0, 0)
        self._mouse_pressed = False
        self._mouse_moved = False

        self._event_time = millis()

    def poll(self):
        self._event_time = millis()
        
        self._key_data = self._keyboard.key_data

        self._mouse_moved = (self._mouse_pos != self._mouse.mouse_pos)
        self._mouse_pos = self._mouse.mouse_pos
        self._mouse_pressed = self._mouse.mouse_pressed

    def get_event_time(self):
        return (millis() - self._event_time)

    def any_key_pressed(self):
        return self._key_data.any_key_pressed()

    def key_is_pressed(self, i):
        return self._key_data.is_pressed(i)
    
    def key_pressed(self):
        return False

    def mouse_is_pressed(self):
        return self._mouse_pressed

    def mouse_moved(self):
        return self._mouse_moved

    def mouse_pos(self):
        return self._mouse_pos