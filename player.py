from ray import *
from polygonSide import PolygonSide
from asteroid import Asteroid
import sliceFunction
import math
import copy
import time
import random

# calculate the orientation of rays given center, asteroids, and width and height of the screen
def calculateRays(width, height, particlePos, asteroidList):
    rayList = []
    bounds = [(0, 0),(width, 0),(width, height),(0, height)]
    for boundX, boundY in bounds:
        ray = Ray(particlePos)
        ray.lookAt(boundX, boundY)
        rayList.append(ray)

    for asteroid in asteroidList:
        for asteroidPoint in asteroid.globalPoints:
            # main ray for asteroid points
            pointX, pointY = asteroidPoint
            rayMain = Ray(particlePos)
            rayMain.lookAt(pointX, pointY)
            rayList.append(rayMain)
            # extra rays for walls behind segment point
            offsetAngle1, vectorX1, vectorY1 = calculateOffsetVector(particlePos, asteroidPoint, -1)
            ray1 = Ray(particlePos, vectorX1, vectorY1, offsetAngle1)
            rayList.append(ray1)
            offsetAngle2, vectorX2, vectorY2 = calculateOffsetVector(particlePos, asteroidPoint, 1)
            ray2 = Ray(particlePos, vectorX2, vectorY2, offsetAngle2)
            rayList.append(ray2)

    return calculateClockwiseRayList(rayList) # clockwise for create_polygon() function

# calculates offset direction vector and angle, direction is either 1 or -1
def calculateOffsetVector(particlePos, asteroidPoint, direction):
    asteroidX, asteroidY = asteroidPoint
    particleX, particleY = particlePos
    offsetAngle = ((.001 * direction) + getAngle(particleX - asteroidX, particleY - asteroidY)) % (2 * math.pi)
    vectorX, vectorY = getVector(offsetAngle)
    return offsetAngle, vectorX, vectorY

# sorts the rayList by angle
def calculateClockwiseRayList(rayList):
    return sorted(rayList, key = rayAngle, reverse = True)

# key for calculateClockwiseRayList
def rayAngle(ray):
    return ray.angle

# takes in a list of rays and list of sides + boundaries and returns the 
# intersection points of the raycasts
def calculateIntersectList(rayList, asteroidList, boundaryList):
    intersectList = []
    sideList = calculateSides(asteroidList)
    for ray in rayList:
        rayX, rayY = ray.point
        minCast = None
        minCastDistance = None
        for side in sideList + boundaryList:
            castValue = ray.cast(side)
            if castValue != None: 
                intersectX, intersectY = castValue
                currentDistance = distance(intersectX, intersectY, rayX, rayY)
                if (minCast == None or currentDistance < minCastDistance):
                    minCast = intersectX, intersectY
                    minCastDistance = currentDistance
        intersectList.append(minCast)
    return intersectList

# takes in asteroid instance and returns its sides
def calculateSides(asteroidList):
    sideList = []
    for asteroid in asteroidList:
        sideList += asteroid.sides
    return sideList

# distance function
def distance(x1, y1, x2, y2):
    return ((x1-x2)**2 + (y1-y2)**2)**.5

def globalToLocal(points, cx, cy): # canvas coordinates to centroid
    result = copy.deepcopy(points)
    for i in range(len(result)):
        x, y = result[i]
        result[i] = [x-cx, y-cy]
    return result

def localToGlobal(points, cx, cy): # centroid coordinates to canvas
    result = copy.deepcopy(points)
    for i in range(len(result)):
        x, y = result[i]
        result[i] = [x+cx, y+cy]
    return result

def addVector(v1, v2):
    return [v1[0] + v2[0], v1[1] + v2[1]]

def subtractVector(v1, v2):
    return [v1[0] - v2[0], v1[1] - v2[1]]

def multiplyVector(v, n):
    return [v[0] * n, v[1] * n]

def divideVector(v, n):
    return [v[0] / n, v[1] / n]

# player class, handles controls, and player displays
class Player(object):
    # pos is a list of x and y and angle in the direction in radians
    def __init__(self, pos, angle, points, health):
        self.pos = pos
        self.angle = angle
        self.points = points
        self.movementVector = [0,0]
        self.globalPoints = localToGlobal(self.points, pos[0], pos[1])
        self.health = health
        self.maxhealth = health
        self.score = 0
        # raycasting
        self.intersectList = []

    # moves the particle given a set of inputs 
    def updateMovement(self, inputs):
        if 'w' in inputs:
            self.updateVelocity()
        if 's' in inputs:
            self.applyFriction()
        if 'a' in inputs:
            self.rotate(1)
        if 'd' in inputs:
            self.rotate(-1)

    def applyFriction(self):
        friction = .02
        if self.movementVector[0] > 0:
            self.movementVector[0] -= friction
        else:
            self.movementVector[0] += friction

        if self.movementVector[1] > 0:
            self.movementVector[1] -= friction
        else:
            self.movementVector[1] += friction

    def updateVelocity(self):
        maxSpeed = 1
        acceleration = .02
        dx, dy = getVector(self.angle)
        self.movementVector[0] += dx * acceleration
        self.movementVector[1] -= dy * acceleration # -= dy because origin is top left
        # checks max velovity in positive direction
        if self.movementVector[0] > maxSpeed:
            self.movementVector[0] = maxSpeed
        if self.movementVector[1] > maxSpeed:
            self.movementVector[1] = maxSpeed
        # checks max velocity in negative direction
        if self.movementVector[0] < -maxSpeed:
            self.movementVector[0] = -maxSpeed
        if self.movementVector[1] < -maxSpeed:
            self.movementVector[1] = -maxSpeed

    def rotate(self, direction):
        rotateSpeed = 2*math.pi/180
        # changes angle
        self.angle = (self.angle + rotateSpeed * direction) % (2*math.pi) 
        cx, cy = self.pos
        # rotates global points
        for point in self.globalPoints: 
            px, py = point
            point[0] = math.cos(rotateSpeed * -direction) * (px - cx) - math.sin(rotateSpeed * -direction) * (py - cy) + cx
            point[1] = math.sin(rotateSpeed * -direction) * (px - cx) + math.cos(rotateSpeed * -direction) * (py - cy) + cy
        # changes position of local points
        self.points = globalToLocal(self.globalPoints, cx, cy) 

    def move(self, app):
        self.pos[0] = (self.pos[0] + self.movementVector[0]) % app.width # movement in the x direction
        self.pos[1] = (self.pos[1] + self.movementVector[1]) % app.height # movement in the y direction
        self.globalPoints = localToGlobal(self.points, self.pos[0], self.pos[1])

    def updateIntersectList(self, app):
        rayList = calculateRays(app.width, app.height, self.pos, app.asteroids)
        self.intersectList = calculateIntersectList(rayList, app.asteroids, app.boundaryList)

    def update(self, app):
        self.updateMovement(app.inputs)
        self.move(app)
        self.updateIntersectList(app)

    def shoot(self, app):
        p0 = copy.deepcopy(self.pos)
        p1 = self.getBoundaryIntersection(app)
        self.applyShootForce()
        i = 0
        while i < len(app.asteroids):
            asteroid = app.asteroids[i]
            ax, ay = asteroid.pos
            if(sliceFunction.sliceIntersectsPolygon(asteroid.globalPoints, p0, p1)):
                self.score += 100
                self.sliceAsteroid(app, asteroid, i, p0, p1, app.width, app.height)
                i += 1
            i += 1
        return p0, p1

    def applyShootForce(self):
        force = 1
        forceVector = getVector(self.angle + math.pi)
        self.movementVector[0] += forceVector[0] * force
        self.movementVector[1] -= forceVector[1] * force

    def getBoundaryIntersection(self, app):
        vectorX, vectorY = getVector(self.angle)
        # negative vector for x
        shootRay = Ray(self.pos, -vectorX, vectorY, self.angle)
        for boundary in app.boundaryList:
            intersectPoint = shootRay.cast(boundary)
            if intersectPoint != None:
                return intersectPoint
        return self.pos # no intersections, should be impossible

    def sliceAsteroid(self, app, asteroid, i, p0, p1, width, height):
        (asteroid1, asteroid2) = asteroid.slice(p0, p1, width, height)
        app.asteroids.pop(i)
        app.asteroids.insert(i,asteroid1)
        app.asteroids.insert(i,asteroid2)
        self.handleExplosion(app, asteroid)

    def handleExplosion(self, app, asteroid):
        asteroidDistance = distance(self.pos[0], self.pos[1], asteroid.pos[0], asteroid.pos[1])
        angleRange = 60 * math.pi/180 # 60 degrees
        amount = random.randint(4, 7)
        for i in range(amount):
            # position
            x, y = getVector(self.angle)
            positionVector = addVector(multiplyVector((x, -y), asteroidDistance), self.pos)
            # velocity
            randomAngle = self.angle + random.uniform(-angleRange, angleRange)
            velocity = random.uniform(1, 5)
            velocityVector = multiplyVector(getVector(randomAngle), velocity)
            dx, dy = velocityVector
            # shape
            shapeIndex = random.randrange(len(app.asteroidShapes))
            newShape = copy.deepcopy(app.asteroidShapes[shapeIndex])
            for i in range(len(newShape)):
                point = newShape[i]
                point = divideVector(point, 75000/asteroid.area+1)
                newShape[i] = point
            # add explosion
            app.explosions.append(Asteroid(newShape, positionVector, (dx, -dy), False))

    # uses ray casting to determine if a point is in polygon
    def inAsteroid(self, app):
        intersectRay = Ray((self.pos[0], self.pos[1]))
        intersectRay.lookAt(app.width + 100, app.height + 100)
        projectileList = app.asteroids + app.alienShots
        for projectile in projectileList:
            numIntersections = 0
            for side in projectile.sides:
                castValue = intersectRay.cast(side)
                if castValue != None:
                    numIntersections += 1
            if numIntersections % 2 == 1:
                return True
        return False

    def removeHealth(self, amount):
        self.health -= amount

    def show(self, app, canvas):
        if len(self.intersectList) > 0:
            canvas.create_polygon(self.intersectList, fill = 'white')
        canvas.create_polygon(self.globalPoints, fill = 'black')

    def drawHealth(self, app, canvas):
        baseMargin = 10
        baseLength = app.width/4
        baseWidth = 20
        canvas.create_rectangle(baseMargin, baseMargin, baseMargin + baseLength, baseMargin + baseWidth, fill = 'black')
        healthMargin = .8
        healthLength = (baseLength - (2 * healthMargin)) * self.health/self.maxhealth
        canvas.create_rectangle(baseMargin + healthMargin, 
                                baseMargin + healthMargin, 
                                baseMargin + healthMargin + healthLength, 
                                baseMargin + baseWidth - healthMargin, 
                                fill = 'white')
    
    def drawScore(self, app, canvas):
        margin = 10
        canvas.create_text(app.width - margin, margin, anchor = "ne", text = self.score, font= 'System 18')