from ray import *
from polygonSide import PolygonSide
import sliceFunction
import math
import copy

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
            if ray.cast(side) != None: 
                intersectX, intersectY = ray.cast(side)
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

class Player(object):
    # pos is a list of x and y and angle in the direction in radians
    def __init__(self, pos, angle, points):
        self.pos = pos
        self.angle = angle
        self.points = points
        self.movementVector = [0,0]
        self.globalPoints = localToGlobal(self.points, pos[0], pos[1])
        self.intersectList = []

    # moves the particle given a set of inputs 
    def updateMovement(self, inputs):
        speed = 3
        rotateSpeed = 2*math.pi/180
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
        maxSpeed = 2
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

    def move(self):
        self.pos[0] += self.movementVector[0] # movement in the x direction
        self.pos[1] += self.movementVector[1] # movement in the y direction
        self.globalPoints = localToGlobal(self.points, self.pos[0], self.pos[1])

    def updateIntersectList(self, app):
        rayList = calculateRays(app.width, app.height, self.pos, app.asteroids)
        self.intersectList = calculateIntersectList(rayList, app.asteroids, app.boundaryList)

    def update(self, app):
        self.updateMovement(app.inputs)
        self.move()
        self.updateIntersectList(app)

    def shoot(self, app):
        p0 = self.pos
        p1 = getBoundaryIntersection(app)
        i = 0
        while i < len(app.asteroids):
            asteroid = app.asteroids[i]
            ax, ay = asteroid.pos
            if(sliceFunction.sliceIntersectsPolygon(asteroid.globalPoints, p0, p1)):
                #sliceFruit(app, f, i, p0, p1, app.width, app.height)
                i += 1
            i += 1

    def getBoundaryIntersection(self, app):
        vectorX, vectorY = getVector(self.angle)
        shootRay = Ray(self.pos, vectorX, vectorY, self.angle)
        for boundary in app.boundaryList:
            intersectPoint = ray.cast(boundary)
            if intersectPoint != None:
                return intersectPoint
        return self.pos # no intersections

    def show(self, app, canvas):
        if len(self.intersectList) > 0:
            canvas.create_polygon(self.intersectList, fill = 'white')
        canvas.create_polygon(self.globalPoints, fill = 'black')
