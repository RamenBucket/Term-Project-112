import centroid
import math
import copy 
import sliceFunction
from polygonSide import PolygonSide

def getVelVectors(slope):
        vel = 1.3 # magnitude of velocity imparted 
        angle = math.atan(slope)
        vx1, vy1 = math.cos(angle)*vel,math.sin(angle)*vel
        return (vx1, vy1) # first coordinate is always on the right

# shifts points around a centroid
def shiftPoints(points):
        newPoints = copy.deepcopy(points)
        xShift, yShift = centroid.find_centroid(newPoints)
        for i in range(len(newPoints)):
            pX, pY = newPoints[i]
            newPoints[i] = (pX - xShift, pY - yShift)
        return newPoints

# canvas coordinates to centroid
def globalToLocal(points,cx,cy): 
    result = copy.deepcopy(points)
    for i in range(len(result)):
        (x,y) = result[i]
        result[i] = (x-cx, y-cy)
    return result

# centroid coordinates to canvas
def localToGlobal(points,cx,cy): 
    result = copy.deepcopy(points)
    for i in range(len(result)):
        (x,y) = result[i]
        result[i] = (x+cx, y+cy)
    return result

def getSides(points):
    sideList = []
    for i in range(len(points)):
        point1 = points[i]
        point2 = points[(i+1)%len(points)]

        side = PolygonSide(point1, point2)
        sideList.append(side)
    return sideList

def getArea(points):
    total = 0
    # iterates throug the list, and adds based on the formula
    for i in range(len(points)):
        x1, y1 =  points[i]
        x2, y2 = points[(i + 1) % len(points)] # mod here is for wrap around
        total += (x1 * y2) - (y1 * x2)
    return abs(total / 2)

# asteroid from hack 112 project (changed fruit.py)
# https://github.com/RamenBucket/112-Hackathon-20
class Asteroid(object):
    def __init__(self, points, pos, vel, uncut):
        self.pos = pos
        self.points = shiftPoints(points)
        self.area = getArea(points)
        cx, cy = pos
        self.globalPoints = localToGlobal(self.points,cx,cy)
        self.sides = getSides(self.globalPoints)
        self.vel = vel
        self.uncut = uncut
    
    def slice(self, p0, p1, width, height):
        (x,y) = self.pos
        
        # convert points to global, slice, convert back to local
        globPoints = localToGlobal(self.points,x,y)
        
        (points1, points2) = sliceFunction.slicePoly(globPoints, p0, p1, width, height)
        points1 = globalToLocal(points1,x,y) # points around old center
        points2 = globalToLocal(points2,x,y)
        
        # shift new center of mass
        (xShift1, yShift1) = centroid.find_centroid(points1)
        (xShift2, yShift2) = centroid.find_centroid(points2)

        pos1 = (x+xShift1, y+yShift1) 
        pos2 = (x+xShift2, y+yShift2)
        
        # Shift points to new centers of masses
        for i in range(len(points1)):
            (pX, pY) = points1[i]
            points1[i] = (pX - xShift1, pY - yShift1)

        for i in range(len(points2)):
            (pX, pY) = points2[i]
            points2[i] = (pX - xShift2, pY - yShift2)

        # Compute velocity direction
        velSlope = 0
        try:
            (cutX0, cutY0), (cutX1, cutY1) = p0, p1
            cutSlope = (cutY1-cutY0) / (cutX1-cutX0)
            velSlope = -1/cutSlope # perpendicular
        except:
            velSlope = 99999

        # change velocities
        (dvx,dvy) = getVelVectors(velSlope) # change in velocity ,(dvx2,dvy2))
        (vx, vy) = self.vel # original velocity
        vel1, vel2 = self.vel, self.vel # initialize vars

        (x1, y1), (x2, y2) = pos1, pos2 # original positions

        if(x1>x2): # poly1 is moving to the right
            vel1 = (vx+dvx, vy+dvy) 
            vel2 = (vx-dvx, vy-dvy)
        else: # poly2 is moving right
            vel1 = (vx-dvx, vy-dvy) 
            vel2 = (vx+dvx, vy+dvy)

        a1 = Asteroid(points1, pos1, vel1, False)
        a2 = Asteroid(points2, pos2, vel2, False)
        return (a1, a2)

    def move(self): # grav = pixels/frame, pre-calculated
        (dx, dy) = self.vel
        (x,y) = self.pos
        self.pos = (x+dx, y+dy) # change position based on velocity
        self.globalPoints = localToGlobal(self.points,x+dx,y+dy)
        self.sides = getSides(self.globalPoints)