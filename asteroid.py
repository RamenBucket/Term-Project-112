import centroid
import math
import copy 
import sliceFunction
from polygonSide import PolygonSide

def getVelVectors(slope):
        vel = 2 #magnitude of velocity imparted
        angle = math.atan(slope)
        vx1, vy1 = math.cos(angle)*vel,math.sin(angle)*vel
        #vx2, vy2 = math.cos(angle+math.pi)*vel,math.sin(angle+math.pi)*vel
        return (vx1,vy1)#,(vx2,vy2) #first coordinate is always on the right

def globalToLocal(points,cx,cy): #canvas coordinates to centroid
    result = copy.deepcopy(points)
    for i in range(len(result)):
        (x,y) = result[i]
        result[i] = (x-cx, y-cy)
    return result

def localToGlobal(points,cx,cy): #centroid coordinates to canvas
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

class Asteroid(object):
    def __init__(self, points, pos, vel, asteroidType, uncut):
        self.points = points
        self.pos = pos
        cx, cy = pos
        self.globalPoints = localToGlobal(self.points,cx,cy)
        self.sides = getSides(self.globalPoints)
        self.vel = vel
        self.asteroidType = asteroidType
        self.uncut = uncut
    
    def slice(self, p0, p1, width, height):
        (x,y) = self.pos
        
        #convert points to global, slice, convert back to local
        globPoints = localToGlobal(self.points,x,y)
        
        (points1, points2) = sliceFunction.slicePoly(globPoints, p0, p1, width, height)
        points1 = globalToLocal(points1,x,y) #points around old center
        points2 = globalToLocal(points2,x,y)
        
        #shift new center of mass
        (xShift1, yShift1) = centroid.find_centroid(points1)
        (xShift2, yShift2) = centroid.find_centroid(points2)

        pos1 = (x+xShift1, y+yShift1) 
        pos2 = (x+xShift2, y+yShift2)
        
        #Shift points to new centers of masses
        for i in range(len(points1)):
            (pX, pY) = points1[i]
            points1[i] = (pX - xShift1, pY - yShift1)

        for i in range(len(points2)):
            (pX, pY) = points2[i]
            points2[i] = (pX - xShift2, pY - yShift2)

        #Compute velocity direction
        velSlope = 0
        try:
            (cutX0, cutY0), (cutX1, cutY1) = p0, p1
            cutSlope = (cutY1-cutY0)/(cutX1-cutX0)
            velSlope = -1/cutSlope #perpendicular
        except:
            velSlope = 99999

        #change velocities
        (dvx,dvy) = getVelVectors(velSlope) #change in velocity ,(dvx2,dvy2))
        (vx, vy) = self.vel #original velocity
        vel1, vel2 = self.vel, self.vel #initialize vars

        (x1,y1), (x2,y2) = pos1, pos2 #original positions
        if(x1>x2): #poly1 is moving to the right
            vel1 = (vx+dvx, vy+dvy) 
            vel2 = (vx-dvx, vy-dvy)
        else: #poly2 is moving right
            vel1 = (vx-dvx, vy-dvy) 
            vel2 = (vx+dvx, vy+dvy)

        f1 = Asteroid(points1,pos1,vel1,self.asteroidType,False)
        f2 = Asteroid(points2,pos2,vel2,self.asteroidType,False)
        return (f1, f2)

    def move(self): #grav = pixels/frame, pre-calculated
        (dx, dy) = self.vel
        (x,y) = self.pos
        self.pos = (x+dx, y+dy) #change position based on velocity
        self.globalPoints = localToGlobal(self.points,x+dx,y+dy)
        self.sides = getSides(self.globalPoints)

#global to center of mass - each coordinate is defined relative to the centroid
# ex) centroid is (122,122) -- coordinates aree  (+1,-2),(-5,+7)

