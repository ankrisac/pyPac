class Key(object):
    BEGIN = 0
    BACKSPACE = BEGIN

    RETURN = BACKSPACE + 1
    ESCAPE = RETURN + 1
    DELETE = RETURN + 2

    UP    = DELETE + 1
    DOWN  = UP + 1
    LEFT  = UP + 2
    RIGHT = UP + 3

    TAB   = RIGHT + 1
    SHIFT = TAB + 1
    CTRL  = TAB + 2
    ALT   = TAB + 3

    KEY_END = ALT + 1

def isKey(key):
    return isinstance(i, str) and len(i) == 1

def isSpecialKey(key):
    return Key.BEGIN <= key < Key.KEY_END and isinstance(key, int)

def key_to_str(i):
    if isSpecialKey(i):
        return "SPECIAL KEY"
    elif isKey(key)
        return i
    else:
        return "ERROR"

class KeyBoard_Event(object):
    def __init__(self):
        self.special_key_begin = 256
        self.key_val = [False for x in range(0, 256 + (Key.END - Key.BEGIN))]

    def _set_key(self, val):
        for i in range(0, self.special_key_begin):
            if key == chr(i):
                self.key_val[i] = val
        if key == CODED:
            lst = [BACKSPACE, RETURN, ESC, DELETE, UP, DOWN, LEFT, RIGHT, TAB, SHIFT, CONTROL, ALT]
            for i in Key:
                if key == lst[i]:
                    self.key_val[i + self.special_key_begin] = val

    def press(self):
        self._set_key(True)

    def release(self):
        self._set_key(False)

    def is_pressed(self, i):
        if isSpecialKey(i):
            return self.key_val[self.skey_begin + i]
        elif type(i) == str and len(i) == 1:
            return self.key_val[ord(i)]
        else:
            return False

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
        
        self._key_val = self._keyboard.key_val

        self._mouse_moved = (self._mouse_pos != self._mouse.mouse_pos)
        self._mouse_pos = self._mouse.mouse_pos
        self._mouse_pressed = self._mouse.mouse_pressed

    def get_event_time(self):
        return (millis() - self._event_time)

    def key_is_pressed(self, i):
        return self._key_val[ord(i)]
    
    def key_pressed(self):
        for i in range(0, len(self._key_val)):
            if self._key_val[ord[i]]:
                return i
        return None

    def mouse_is_pressed(self):
        return self._mouse_pressed

    def mouse_moved(self):
        return self._mouse_moved

    def mouse_pos(self):
        return self._mouse_pos