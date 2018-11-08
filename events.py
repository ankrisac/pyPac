class KeyBoard_Event(object):
    def __init__(self):
        self.key_val = [False for x in range(0, 256)]

    def press(self):
        for i in range(0, len(self.key_val)):
            if key == chr(i):
                self.key_val[i] = True

    def release(self):
        for i in range(0, len(self.key_val)):
            if key == chr(i):
                self.key_val[i] = False

    def is_pressed(self, i):
        return self.key_val[ord(i)]

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
    KEY_UP = "w"
    KEY_DOWN = "s"
    KEY_LEFT = "a"
    KEY_RIGHT = "d"
    KEY_ENTER = ENTER

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
        if isinstance(i, list):
            for iter in i:
                if self._key_val[ord(i)]:
                    return True
            return False
        else:
            return self._key_val[ord(i)]

    def mouse_is_pressed(self):
        return self._mouse_pressed

    def mouse_moved(self):
        return self._mouse_moved

    def mouse_pos(self):
        return self._mouse_pos
