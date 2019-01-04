import math
import time
import events

begin_time = time.time()

def get_millis():
    return int(round((time.time() - begin_time) * 1000))

def get_framerate():
    return events.get_framerate()

class Error(object):
    log_error = True

    log_file = open("crash_dump.txt", "w")
    log_file.write("Crash Dump")
    
    count = 0

    @staticmethod
    def log(*args):
        if Error.count == 0:
            Error.log_file.write("Report")

        msg = ""

        for i in args:
            msg += str(i) + ": "

        msg = "Err #{0} : {1}".format(Error.count, msg)

        Error.log_file.write(msg + "\n")
        print(msg)
        
        Error.count += 1

class Vec(object):
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vec(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec(self.x - other.x, self.y - other.y)
    
    def __mul__(self, other):
        if isinstance(other, Vec):
            return Vec(self.x * other.x, self.y * other.y)
        else:
            return Vec(self.x * other, self.y * other)

    def __truediv__(self, other):
        if isinstance(other, Vec):
            return Vec(self.x / other.x, self.y / other.y)
        else:
            return Vec(self.x / other, self.y / other)

    def __iter__(self):
        return (x for x in [self.x, self.y])

    def __str__(self):
        return "[{0},{1}]".format(self.x, self.y)

    def magsq(self):
        return self.x * self.x + self.y * self.y

    def mag(self):
        return math.sqrt(self.magsq())

    def mag_manhattan(self):
        return abs(self.x) + abs(self.y)

    def mag_chebyshev(self):
        return max(abs(self.x), abs(self.y))

    def norm(self):
        mag = self.mag()
        return self.__mul__(0 if mag == 0 else (1/mag))

    def apply(self, func):
        return Vec(func(self.x), func(self.y))

    def angle(self):
        return math.atan2(self.y, self.x)
    
    def is_zero(self):
        return (self.x == 0 and self.y == 0)

    def unpack(self):
        return (self.x, self.y)
