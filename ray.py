import math

# returns angle in radians given direction vector
def getAngle(x, y):
    # if the line is vertial
    if x == 0 and y <= 0:
        return 3 * math.pi/2
    elif x == 0 and y >= 0:
        return math.pi/2 
    # other cases for arctan function
    elif x >= 0 and y >= 0:
        return math.atan(abs(y/x))
    elif x <= 0 and y >= 0:
        return math.pi/2 + (math.pi/2 - math.atan(abs(y/x)))
    elif x <= 0 and y <= 0:
        return math.pi + math.atan(abs(y/x))
    else:
        return 3*(math.pi/2) + (math.pi/2 - math.atan(abs(y/x)))

# returns direction vector given angle in radians
def getVector(angle):
    return (math.cos(angle), math.sin(angle))

# from https://thecodingtrain.com/CodingChallenges/145-2d-ray-casting.html
class Ray(object):
    def __init__(self, point, directionX = 1, directionY = 0, angle = math.pi/2):
        self.point = point
        self.directionX = directionX
        self.directionY = directionY
        self.angle = angle

    # takes in a point and orients the ray towards that point
    def lookAt(self, x, y):
        # calculate direction vector by dividing by magnitude
        self.directionX = (self.point[0] - x) / (((self.point[0] - x)**2 + (self.point[1] - y)**2)**.5)
        self.directionY = (self.point[1] - y) / (((self.point[0] - x)**2 + (self.point[1] - y)**2)**.5)
        self.angle = getAngle(self.directionX, self.directionY)

    # casts ray at a side and returns intersection point
    def cast(self, polygonSide):
        x1 = polygonSide.point1[0]
        y1 = polygonSide.point1[1]
        x2 = polygonSide.point2[0]
        y2 = polygonSide.point2[1]

        x3 = self.point[0]
        y3 = self.point[1]
        x4 = self.point[0] + self.directionX
        y4 = self.point[1] + self.directionY
        
        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denominator == 0: return None

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
        u = ((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator
        # not exactly 0 or 1 because of point errors
        if t >= -.0001 and t <= 1.0001 and u >= -.0001:
            intersectPoint = (x1 + (t * (x2 - x1)), y1 + (t * (y2 - y1)))
            return intersectPoint
        else:
            return None
