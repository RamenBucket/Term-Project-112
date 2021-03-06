# Sources (also cited before the specific sections in the code)
# https://www.red3d.com/cwr/boids/
# https://github.com/RamenBucket/112-Hackathon-20
# https://ncase.me/sight-and-light/
# https://thecodingtrain.com/CodingChallenges/124-flocking-boids
# http://rosettacode.org/wiki/Sutherland-Hodgman_polygon_clipping#Python
# https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#installingModules
# https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
# https://thecodingtrain.com/CodingChallenges/145-2d-ray-casting.html

from cmu_112_graphics import *
from asteroid import *
from boid import *
from splashScreen import *
from endScreen import *
from ray import Ray, getAngle, getVector
from polygonSide import PolygonSide
from player import Player
import sliceFunction
import orderClockwise
import centroid
import math
import time
import random

class GameMode(Mode):
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
        # player
        playerPos = [mode.width/2, mode.height/2]
        playerAngle = math.pi/2
        playerHealth = 100
        mode.playerShape = [[0,-20],[10,10],[0,5],[-10,10]]
        mode.player = Player(playerPos, playerAngle, mode.playerShape, playerHealth)
        mode.inputs = set()
        # player shooting
        mode.shotP1 = None
        mode.shotP2 = None
        mode.lastShotTime = None
        mode.totalShotTime = .5
        mode.playerIsShooting = False
        # player health
        mode.lastRemoveHealthTime = time.time()
        mode.totalRemoveHealthTime = .05
        # aliens
        mode.flock = []
        mode.initFlock(15)
        mode.alienShots = []
        # backgrounds
        bg = mode.loadImage('bg0.png')
        mode.bg = ImageTk.PhotoImage(bg)
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
        controls = {'w', 'a', 's', 'd'}
        if event.key in controls:
            mode.inputs.add(event.key)
        if event.key == 'Space':
            if not mode.playerIsShooting:
                mode.shotP1, mode.shotP2 = mode.player.shoot(mode)
                mode.lastShotTime = time.time()
                mode.playerIsShooting = True
        
    def keyReleased(mode, event):
        controls = {'w', 'a', 's', 'd'}
        if event.key in controls:
            mode.inputs.add(event.key) # for error when switching app modes
            mode.inputs.remove(event.key)

    def timerFired(mode):
        mode.handleAsteroids() # asteroid must update before player raycasting 
        mode.handlePlayer()
        mode.handleFlock()

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

    #################
    # player update #
    #################
    def handlePlayer(mode):
        mode.player.update(mode) # movement and raycasting
        mode.shotTimer() # shooting
        if mode.player.inAsteroid(mode): # health
            mode.doRemoveHealth()
            if mode.player.health < 0:
                mode.handleLeaderboard()
                mode.app.setActiveMode(mode.app.endScreenMode)
                mode.app.endScreenMode.appStarted()

    def shotTimer(mode):
        if mode.playerIsShooting:
            if (mode.lastShotTime == None) or (time.time() - mode.lastShotTime > mode.totalShotTime):
                mode.playerIsShooting = False

    def doRemoveHealth(mode):
        if (time.time() - mode.lastRemoveHealthTime > mode.totalRemoveHealthTime):
            mode.lastRemoveHealthTime = time.time()
            mode.player.removeHealth(1)

    def handleLeaderboard(mode):
        # reading the file and converting it into list of ints
        scores = open('scores.txt', 'r')
        intScoreList = [int(score) for score in scores.read().splitlines()]
        scores.close()
        # adding current score and sorting 
        intScoreList.append(mode.player.score)
        intScoreList.sort(reverse=True)
        # convert back to string and writes top 5 scores to file
        newScoreList = [str(score) + '\n' for score in intScoreList[0:5]]
        scores = open('scores.txt', 'w')
        scores.writelines(newScoreList)
        scores.close()

    ################
    # flock update #
    ################
    def handleFlock(mode):
        for boid in mode.flock: # flock update
            boid.flock(mode.flock, mode.asteroids, mode.player)
            boid.update(mode)
            boid.shoot(mode)
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
        # game
        mode.drawBackground(canvas)
        mode.drawAsteroids(canvas)
        mode.drawPlayer(canvas)
        mode.drawExplosions(canvas)
        mode.drawAliens(canvas)
        # UI
        mode.player.drawHealth(mode, canvas)
        mode.player.drawScore(mode, canvas)

    def drawBackground(mode, canvas):
        canvas.create_image(mode.width/2, mode.height/2, image = mode.bg)

    def drawAsteroids(mode, canvas):
        for asteroid in mode.asteroids:
            asteroidX, asteroidY = asteroid.pos
            coords = localToGlobal(asteroid.points, asteroidX, asteroidY)
            canvas.create_polygon(coords, outline = 'white', width = 1)

    def drawExplosions(mode, canvas):
        for explosion in mode.explosions:
            explosionX, explosionY = explosion.pos
            coords = localToGlobal(explosion.points, explosionX, explosionY)
            canvas.create_polygon(coords, outline = 'white', width = 1)

    def drawPlayer(mode, canvas):
        mode.player.show(mode, canvas)
        if mode.playerIsShooting:
            x0, y0 = mode.shotP1
            x1, y1 = mode.shotP2
            # makes the line shrink after it it shot
            currWidth = mode.totalShotTime / ((time.time() - mode.lastShotTime) + .01) 
            canvas.create_line(x0, y0, x1, y1, fill = 'black', width = currWidth)

    def drawAliens(mode, canvas):
        for boid in mode.flock:
            boid.show(mode, canvas)
        mode.drawAlienShots(canvas)

    def drawAlienShots(mode, canvas):
        for shot in mode.alienShots:
            shotX, shotY = shot.pos
            coords = localToGlobal(shot.points, shotX, shotY)
            canvas.create_polygon(coords, outline = 'white', width = 1)

class Asteroids(ModalApp):
    def appStarted(app):
        app.gameMode = GameMode()
        app.splashScreenMode = SplashScreenMode()
        app.endScreenMode = EndScreenMode()
        app.setActiveMode(app.splashScreenMode)

app = Asteroids(width=1024, height=1024)