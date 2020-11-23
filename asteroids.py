from cmu_112_graphics import *
from asteroid import *
from ray import Ray, getAngle, getVector
from polygonSide import PolygonSide
from player import Player
import sliceFunction
import orderClockwise
import centroid
import math
import time
import copy

asteroidOutlines = [
    [(-50,0),(-35,35),(0,50),(35,35),(50,0),(35,-35),(0,-50),(-35,-35)],
    [(50,50),(50,-50),(-50,-50),(-50,50)],
    [(-100,0),(-70,70),(0,100),(70,70),(100,0),(70,-70),(0,-100),(-70,-70)],
    [(-50,0),(-35,30),(0,40),(35,30),(50,0),(35,-30),(0,-40),(-35,-30)],
    [(-50,0),(-35,30),(0,40),(35,30),(50,0),(35,-30),(0,-40),(-35,-30)],
    [(-50,0),(-28,28),(0,50),(28,28),(50,0),(35,-35),(0,-50),(-35,-35)]
]

asteroidTypes = [
    "big",
    "medium",
    "small"
]

playerShape = [[0,-20],[10,10],[0,5],[-10,10]]

def appStarted(app):
    # asteroids
    app.asteroids = []
    initAsteroids(app)
    # boundary
    app.boundaryList = [PolygonSide((0,0),(app.width,0)),
                        PolygonSide((app.width,0),(app.width,app.height)),
                        PolygonSide((app.width,app.height),(0,app.height)),
                        PolygonSide((0,app.height),(0,0))]
    # player
    playerPos = [app.width/2, app.height/2]
    playerAngle = math.pi/2
    app.player = Player(playerPos, playerAngle, playerShape)
    app.inputs = set()
    # background
    bg = app.loadImage('space_bg.png')
    app.bg = ImageTk.PhotoImage(bg)
    # timer
    app.timerDelay = 1
    app.mouseMovedDelay = 2

# ititalizes asteroid objects
def initAsteroids(app):
    newAsteroid = Asteroid(asteroidOutlines[1], (app.width/2, app.height/4), (0,0), asteroidTypes[1], False)
    newAsteroid1 = Asteroid(asteroidOutlines[0], (app.width/4, app.height/2), (0,0), asteroidTypes[1], False)
    newAsteroid2 = Asteroid(asteroidOutlines[1], (app.width/2, 3*app.height/4), (0,0), asteroidTypes[1], False)
    newAsteroid3 = Asteroid(asteroidOutlines[0], (3*app.width/4, app.height/2), (0,0), asteroidTypes[1], False)
    app.asteroids.append(newAsteroid)
    app.asteroids.append(newAsteroid1)
    app.asteroids.append(newAsteroid2)
    app.asteroids.append(newAsteroid3)
            
""" def mouseMoved(app, event):
    app.particlePos = event.x, event.y """

def keyPressed(app, event):
    controls = {'w', 'a', 's', 'd', 'q', 'e'}
    if event.key in controls:
        app.inputs.add(event.key)
    
def keyReleased(app, event):
    controls = {'w', 'a', 's', 'd', 'q', 'e'}
    if event.key in controls:
        app.inputs.remove(event.key)

def timerFired(app):
    app.player.update(app)

    for asteroid in app.asteroids:
        asteroid.move()

def redrawAll(app, canvas):
    drawBackground(app, canvas)
    drawText(app, canvas)
    drawAsteroids(app, canvas)
    # particle
    app.player.show(app, canvas)

def drawBackground(app, canvas):
    canvas.create_image(app.width/2, app.height/2, image = app.bg)

def drawText(app, canvas):
    message = 'The shadows prove the light.'
    canvas.create_text(app.width/2,app.height/2, text=message, font='System', fill = "white")

def drawAsteroids(app, canvas):
    for asteroid in app.asteroids:
        asteroidX, asteroidY = asteroid.pos
        coords = localToGlobal(asteroid.points, asteroidX, asteroidY)
        canvas.create_polygon(coords, outline = 'white', fill = "black", width = 1)

runApp(width=1024, height=1024)