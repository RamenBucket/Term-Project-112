class Boid(object):
    def __init__(self, pos, vel, acc):
        self.pos = pos
        self.vel = vel
        self.acc = acc

    def show(self, app, canvas):
        r = 10
        cx, cy = self.pos
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill = 'black')