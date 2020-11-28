import math

def getAngle(x, y):
    # if the line is vertial
    if x == 0 and y <= 0:
        return 3 * math.pi/2
    elif x == 0 and y >= 0:
        return math.pi/2 
    # other cases for arctan function
    elif x >= 0 and y >= 0:
        return math.atan(abs(y/x))
    elif x <= 0 and y >= 0:
        return math.pi/2 + (math.pi/2 - math.atan(abs(y/x)))
    elif x <= 0 and y <= 0:
        return math.pi + math.atan(abs(y/x))
    else:
        return 3*(math.pi/2) + (math.pi/2 - math.atan(abs(y/x)))

# returns direction vector given angle in radians
def getVector(angle):
    return (math.cos(angle), math.sin(angle))

def addVector(v1, v2):
    return [v1[0] + v2[0], v1[1] + v2[1]]

def subtractVector(v1, v2):
    return [v1[0] - v2[0], v1[1] - v2[1]]

def addVectorWrapAround(v1, v2, w, h):
    return [(v1[0] + v2[0]) % w, (v1[1] + v2[1]) % h]

def multiplyVector(v, n):
    return [v[0] * n, v[1] * n]

def distance(p1, p2):
    return ((p1[0] - p2[0])**2 + (p1[0] - p2[0])**2)**0.5

class Boid(object):
    def __init__(self, pos, vel, acc):
        self.pos = pos
        self.vel = vel
        self.acc = acc
        self.maxForce = .0015
        self.maxCohesionForce = .0015
        self.maxSpeed = 1

    def __eq__(self, other):
        return isinstance(other, Boid) and (self.pos == other.pos and
                                            self.vel == other.vel and
                                            self.acc == other.acc and
                                            self.maxForce == other.maxForce and
                                            self.maxCohesionForce == other.maxCohesionForce and
                                            self.maxSpeed == other.maxSpeed)

    def allign(self, boids):
        perceptionRadius = 100
        steering = [0, 0]
        total = 0
        for boid in boids:
            if boid != self and distance(self.pos, boid.pos) < perceptionRadius:
                steering = addVector(steering, boid.vel)
                total += 1
        if total > 0:
            steering = multiplyVector(steering, 1/total) # divide by total
            steering = multiplyVector(getVector(getAngle(steering[0], steering[1])), self.maxSpeed)
            steering = subtractVector(steering, self.vel) # subtracting
            # limits the magnitude of alignment
            if distance([0,0], steering) > self.maxForce:
                steering = multiplyVector(getVector(getAngle(steering[0], steering[1])), self.maxForce)
        return steering

    def cohesion(self, boids):
        perceptionRadius = 100
        steering = [0, 0]
        total = 0
        for boid in boids:
            if boid != self and distance(self.pos, boid.pos) < perceptionRadius:
                steering = addVector(steering, boid.pos)
                total += 1
        if total > 0:
            steering = multiplyVector(steering, 1/total) # divide by total
            steering = subtractVector(steering, self.pos)
            steering = multiplyVector(getVector(getAngle(steering[0], steering[1])), self.maxSpeed)
            steering = subtractVector(steering, self.vel) # subtracting
            # limits the magnitude of alignment
            if distance([0,0], steering) > self.maxCohesionForce:
                steering = multiplyVector(getVector(getAngle(steering[0], steering[1])), self.maxCohesionForce)
        return steering

    def flock(self, boids):
        self.acc = [0, 0]
        alignment = self.allign(boids)
        cohesion = self.cohesion(boids)
        self.acc = addVector(self.acc, alignment)
        self.acc = addVector(self.acc, cohesion)

    def update(self, app):
        # update position
        self.pos = addVectorWrapAround(self.pos, self.vel, app.width, app.height)
        # update velocity
        self.vel = addVector(self.vel, self.acc)
        if distance([0,0], self.vel) > self.maxSpeed:
            self.vel = multiplyVector(getVector(getAngle(self.vel[0], self.vel[1])), self.maxSpeed)

    def show(self, app, canvas):
        r = 10
        cx, cy = self.pos
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill = 'black')