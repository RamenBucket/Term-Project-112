from cmu_112_graphics import *
from boid import *
import random
import math
import copy

def appStarted(app):
    app.flock = []
    initFlock(app)
    # timer
    app.timerDelay = 1
    app.mouseMovedDelay = 2

def initFlock(app):
    amount = 20
    for i in range(amount):
        pos = [random.randint(0, app.width), random.randint(0, app.height)]
        # gets vector with random direction and magnitude
        vel = multiplyVector(getVector(random.uniform(0, 2*math.pi)), random.uniform(.5, 1))
        acc = [0, 0]
        app.flock.append(Boid(pos, vel, acc))

# returns direction vector given angle in radians
def getVector(angle):
    return [math.cos(angle), math.sin(angle)]

def timerFired(app):
    copyFlock = copy.deepcopy(app.flock)
    for boid in app.flock:
        boid.flock(copyFlock)
        boid.update(app)

def redrawAll(app, canvas):
    for boid in app.flock:
        boid.show(app, canvas)

runApp(width=1024, height=1024)
