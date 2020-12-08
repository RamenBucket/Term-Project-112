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

# this mode shows handles splashscreen events
class SplashScreenMode(Mode):
    def appStarted(mode):
        # asteroids
        mode.asteroids = []
        mode.explosions = []
        mode.asteroidShapes = [
            [(0,50),(50,-50),(-50,-50),(-50,50)],
            [(-50,100),(50,100),(100,0),(50,-100),(-50,-100),(-100,0)],
            [(-50,100),(50,100),(50,-50),(-50,-100),(-100,50)],
            [(-50,100),(50,100),(100,50),(50,-50),(-50,-100),(-100,0)],
            [(0,50),(100,50),(50,-100),(-50,-100),(-50,-50)],
        ]
        # boundary
        mode.boundaryList = [PolygonSide((0,0),(mode.width,0)),
                            PolygonSide((mode.width,0),(mode.width,mode.height)),
                            PolygonSide((mode.width,mode.height),(0,mode.height)),
                            PolygonSide((0,mode.height),(0,0))]
        # aliens
        mode.flock = []
        mode.initFlock(15)
        mode.alienShots = []
        # backgrounds
        bg = mode.loadImage('bg0.png')
        mode.bg = ImageTk.PhotoImage(bg)
        mode.showSubtext = True
        mode.lastSubtextTime = time.time()
        mode.totalSubtextTime = .7
        # timer
        mode.lastWaveTime = time.time()
        mode.timeBetweenWaves = .5

    def initFlock(mode, amount):
        for i in range(amount):
            pos = [random.randint(0, mode.width), random.randint(0, mode.height)]
            # gets vector with random direction and magnitude
            vel = multiplyVector(getVector(random.uniform(0, 2*math.pi)), random.uniform(.5, 1))
            acc = [0, 0]
            mode.flock.append(Boid(pos, vel, acc))

    def keyPressed(mode, event):
        mode.app.setActiveMode(mode.app.gameMode)
        mode.app.gameMode.appStarted()

    def timerFired(mode):
        mode.handleAsteroids() # asteroid must update before player raycasting 
        mode.handleFlock()
        mode.handleSubtext()

    def handleSubtext(mode):
        if (time.time() - mode.lastSubtextTime > mode.totalSubtextTime):
            mode.showSubtext = not mode.showSubtext
            mode.lastSubtextTime = time.time()

    ###################
    # asteroid update #
    ###################
    def handleAsteroids(mode):
        mode.spawnAsteroids() # spawn
        for asteroid in mode.asteroids: # update
            asteroid.move()
        mode.removeAsteroids() # remove
        for explosion in mode.explosions: # update
            explosion.move()
        mode.removeExplosions() # remove

    def spawnAsteroids(mode):
        maxAsteroids = 3
        if (time.time() - mode.lastWaveTime > mode.timeBetweenWaves):
            spawnAmount = max(0,maxAsteroids - len(mode.asteroids))
            mode.createWave(spawnAmount)
            mode.lastWaveTime = time.time()

    def createWave(mode, amount):
        if amount == 0: return 
        margin = 50
        newWave = []
        for i in range(amount):
            # random position
            randomX = random.randint(0 - margin, mode.width + margin)
            randomY = random.randint(0 - margin, mode.height + margin)
            while 0 < randomX < mode.width and 0 < randomY < mode.height:
                randomX = random.randint(0 - margin, mode.width + margin)
                randomY = random.randint(0 - margin, mode.height + margin)
            # random velocity
            if randomX < mode.width/2: 
                xVector = random.uniform(1,1.5)
            else: 
                xVector = -1 * random.uniform(1,1.5)
            if randomY < mode.height/2: 
                yVector = random.uniform(1,1.5)
            else: 
                yVector = -1 * random.uniform(1,1.5)
            # random shape
            asteroidIndex = random.randrange(0, len(mode.asteroidShapes))
            # create random asteroid
            newWave.append(Asteroid(mode.asteroidShapes[asteroidIndex], (randomX, randomY), (xVector, yVector), False))
        mode.asteroids.extend(newWave)

    def removeAsteroids(mode):
        margin = 50
        i = 0
        while i < len(mode.asteroids):
            asteroid = mode.asteroids[i]
            x, y = asteroid.pos
            if not (0 - margin <= x <= mode.width + margin) or not (0 - margin <= y <= mode.height) or asteroid.area < 1000:
                mode.asteroids.pop(i)
            else:
                i += 1

    def removeExplosions(mode):
        margin = 50
        i = 0
        while i < len(mode.explosions):
            explosion = mode.explosions[i]
            x, y = explosion.pos
            if not (0 - margin <= x <= mode.width + margin) or not (0 - margin <= y <= mode.height):
                mode.explosions.pop(i)
            else:
                i += 1

    ################
    # flock update #
    ################
    def handleFlock(mode):
        for boid in mode.flock: # flock update
            boid.flock(mode.flock, mode.asteroids)
            boid.update(mode)
            # boid.shoot(mode)
        for shot in mode.alienShots: # shot update
            shot.move()
        mode.removeShots() # remove

    def removeShots(mode):
        margin = 50
        i = 0
        while i < len(mode.alienShots):
            shot = mode.alienShots[i]
            x, y = shot.pos
            if not (0 - margin <= x <= mode.width + margin) or not (0 - margin <= y <= mode.height):
                mode.alienShots.pop(i)
            else:
                i += 1

    def redrawAll(mode, canvas):
        mode.drawBackground(canvas)
        mode.drawAsteroids(canvas)
        mode.drawAliens(canvas)
        mode.drawUI(canvas)

    def drawBackground(mode, canvas):
        canvas.create_image(mode.width/2, mode.height/2, image = mode.bg)

    def drawAsteroids(mode, canvas):
        for asteroid in mode.asteroids:
            asteroidX, asteroidY = asteroid.pos
            coords = localToGlobal(asteroid.points, asteroidX, asteroidY)
            canvas.create_polygon(coords, outline = 'white', width = 1)

    def drawAliens(mode, canvas):
        for boid in mode.flock:
            boid.show(mode, canvas)
        mode.drawAlienShots(canvas)

    def drawAlienShots(mode, canvas):
        for shot in mode.alienShots:
            shotX, shotY = shot.pos
            coords = localToGlobal(shot.points, shotX, shotY)
            canvas.create_polygon(coords, outline = 'white', width = 1)
    
    def drawUI(mode, canvas):
        title = 'ASTEROIDS'
        canvas.create_text(mode.width/2, mode.height/3, text = title, font= 'System 500', fill = 'white')
        subText = 'PRESS ANY KEY TO BEGIN'
        if mode.showSubtext:
            canvas.create_text(mode.width/2, mode.height*2/3, text = subText, font= 'System 20', fill = 'white')