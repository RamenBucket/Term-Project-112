from cmu_112_graphics import *
from asteroid import *
from boid import *
from ray import Ray, getAngle, getVector
from polygonSide import PolygonSide
from player import Player
import sliceFunction
import orderClockwise
import centroid
import math
import time
import random

asteroidOutlines = [
    [(-50,0),(-35,35),(0,50),(35,35),(50,0),(35,-35),(0,-50),(-35,-35)],
    [(50,50),(50,-50),(-50,-50),(-50,50)]
]

#####################
# recalculate centroids for asteroid shapes
#####################
asteroidShapes = [
    [(0,50),(50,-50),(-50,-50),(-50,50)],
    [(-50,100),(50,100),(100,0),(50,-100),(-50,-100),(-100,0)],
    [(-50,100),(50,100),(50,-50),(-50,-100),(-100,50)],
    [(-50,100),(50,100),(100,50),(50,-50),(-50,-100),(-100,0)],
    [(0,50),(100,50),(50,-100),(-50,-100),(-50,-50)],
]

# below is 2x smaller version of above
""" asteroidShapes = [
    [(0,25),(25,-25),(-25,-25),(-25,25)],
    [(-25,50),(25,50),(50,0),(25,-50),(-25,-50),(-50,0)],
    [(-25,50),(25,50),(25,-25),(-25,-50),(-50,25)],
    [(-25,50),(25,50),(50,25),(25,-25),(-25,-50),(-50,0)],
    [(0,25),(50,25),(25,-50),(-25,-50),(-25,-25)],
] """

playerShape = [[0,-20],[10,10],[0,5],[-10,10]]

def appStarted(app):
    # asteroids
    app.asteroids = []
    # boundary
    app.boundaryList = [PolygonSide((0,0),(app.width,0)),
                        PolygonSide((app.width,0),(app.width,app.height)),
                        PolygonSide((app.width,app.height),(0,app.height)),
                        PolygonSide((0,app.height),(0,0))]
    # player
    playerPos = [app.width/2, app.height/2]
    playerAngle = math.pi/2
    playerHealth = 100
    app.player = Player(playerPos, playerAngle, playerShape, playerHealth)
    app.inputs = set()
    # player shooting
    app.shotP1 = None
    app.shotP2 = None
    app.lastShotTime = None
    app.totalShotTime = .5
    app.playerIsShooting = False
    # player health
    app.lastRemoveHealthTime = time.time()
    app.totalRemoveHealthTime = .05
    # aliens
    app.flock = []
    initFlock(app)
    app.alienShots = []
    # backgrounds
    bg = app.loadImage('space_bg.png')
    app.bg = ImageTk.PhotoImage(bg)
    # timer
    app.lastWaveTime = time.time()
    app.timeBetweenWaves = .5
    app.timerDelay = 1
    app.mouseMovedDelay = 2

def initFlock(app):
    amount = 15
    for i in range(amount):
        pos = [random.randint(0, app.width), random.randint(0, app.height)]
        # gets vector with random direction and magnitude
        vel = multiplyVector(getVector(random.uniform(0, 2*math.pi)), random.uniform(.5, 1))
        acc = [0, 0]
        app.flock.append(Boid(pos, vel, acc))

def spawnAsteroids(app):
    maxAsteroids = 3
    if (time.time() - app.lastWaveTime > app.timeBetweenWaves):
        spawnAmount = max(0,maxAsteroids - len(app.asteroids))
        createWave(app, spawnAmount)
        app.lastWaveTime = time.time()

def createWave(app, amount):
    if amount == 0: return 
    margin = 50
    newWave = []
    for i in range(amount):
        # random position
        randomX = random.randint(0 - margin, app.width + margin)
        randomY = random.randint(0 - margin, app.height + margin)
        while 0 < randomX < app.width and 0 < randomX < app.height:
            randomX = random.randint(0 - margin, app.width + margin)
            randomY = random.randint(0 - margin, app.height + margin)
        # random velocity
        if randomX < app.width: 
            xVector = random.uniform(1,1.5)
        else: 
            xVector = -1 * random.uniform(1,1.5)
        if randomY < app.height: 
            yVector = random.uniform(1,1.5)
        else: 
            yVector = -1 * random.uniform(1,1.5)
        asteroidIndex = random.randrange(0, len(asteroidShapes))
        # create random asteroid
        newWave.append(Asteroid(asteroidShapes[asteroidIndex], (randomX, randomY), (xVector, yVector), False))
    
    app.asteroids.extend(newWave)

def removeAsteroids(app):
    margin = 50
    i = 0
    while i < len(app.asteroids):
        asteroid = app.asteroids[i]
        x, y = asteroid.pos
        if not (0 - margin <= x <= app.width + margin) or not (0 - margin <= y <= app.height):
            app.asteroids.pop(i)
        else:
            i += 1

def removeShots(app):
    margin = 50
    i = 0
    while i < len(app.alienShots):
        shot = app.alienShots[i]
        x, y = shot.pos
        if not (0 - margin <= x <= app.width + margin) or not (0 - margin <= y <= app.height):
            app.alienShots.pop(i)
        else:
            i += 1

def keyPressed(app, event):
    controls = {'w', 'a', 's', 'd', 'q', 'e'}
    if event.key in controls:
        app.inputs.add(event.key)
    if event.key == 'Space':
        if not app.playerIsShooting:
            app.shotP1, app.shotP2 = app.player.shoot(app)
            app.lastShotTime = time.time()
            app.playerIsShooting = True

def shotTimer(app):
    if app.playerIsShooting:
        if (app.lastShotTime == None) or (time.time() - app.lastShotTime > app.totalShotTime):
            app.playerIsShooting = False
    
def keyReleased(app, event):
    controls = {'w', 'a', 's', 'd', 'q', 'e'}
    if event.key in controls:
        app.inputs.remove(event.key)

def timerFired(app):
    spawnAsteroids(app)
    # asteroid run first for update raycasting when slicing
    for asteroid in app.asteroids:
        asteroid.move()
    app.player.update(app)
    shotTimer(app)
    if app.player.inAsteroid(app):
        doRemoveHealth(app)
    for boid in app.flock:
        boid.flock(app.flock, app.asteroids, app.player)
        boid.update(app)
        boid.shoot(app)
    for shot in app.alienShots:
        shot.move()
    removeAsteroids(app)
    removeShots(app)

def doRemoveHealth(app):
    if (time.time() - app.lastRemoveHealthTime > app.totalRemoveHealthTime):
        app.lastRemoveHealthTime = time.time()
        app.player.removeHealth(1)

def redrawAll(app, canvas):
    drawBackground(app, canvas)
    #drawText(app, canvas)
    drawAsteroids(app, canvas)
    # particle
    app.player.show(app, canvas)
    # player shot
    if app.playerIsShooting:
        x0, y0 = app.shotP1
        x1, y1 = app.shotP2
        # width part makes the line shrink after it it shot
        canvas.create_line(x0, y0, x1, y1, fill = 'black', width = app.totalShotTime / ((time.time() - app.lastShotTime) + .01))
    for boid in app.flock:
        boid.show(app, canvas)
    drawAlienShots(app, canvas)
    app.player.drawHealth(app, canvas)
    app.player.drawScore(app, canvas)

def drawBackground(app, canvas):
    canvas.create_image(app.width/2, app.height/2, image = app.bg)

def drawText(app, canvas):
    message = 'The shadows prove the light.'
    canvas.create_text(app.width/2, app.height/2, text=message, font='System', fill = "white")

def drawAsteroids(app, canvas):
    for asteroid in app.asteroids:
        asteroidX, asteroidY = asteroid.pos
        coords = localToGlobal(asteroid.points, asteroidX, asteroidY)
        canvas.create_polygon(coords, outline = 'white', width = 1)

def drawAlienShots(app, canvas):
    for shot in app.alienShots:
        shotX, shotY = shot.pos
        coords = localToGlobal(shot.points, shotX, shotY)
        canvas.create_polygon(coords, outline = 'white', width = 1)

runApp(width=1024, height=1024)