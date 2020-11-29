from cmu_112_graphics import *
from boid import *
from asteroid import *
import random
import math
import copy

def appStarted(app):
    app.asteroids = []
    app.asteroids.append(Asteroid([(-50,0),(-35,35),(0,50),(35,35),(50,0),(35,-35),(0,-50),(-35,-35)], (app.width/2, app.height/2), (0,0), "medium", False))
    app.flock = []
    initFlock(app)
    # timer
    app.timerDelay = 1
    app.mouseMovedDelay = 2

def initFlock(app):
    amount = 30
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
    for boid in app.flock:
        boid.flock(app.flock, app.asteroids)
        boid.update(app)

def redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = 'black')
    for boid in app.flock:
        boid.show(app, canvas)

    for asteroid in app.asteroids:
        asteroidX, asteroidY = asteroid.pos
        coords = localToGlobal(asteroid.points, asteroidX, asteroidY)
        canvas.create_polygon(coords, outline = 'white', fill = "black", width = 1)

runApp(width=512, height=512)