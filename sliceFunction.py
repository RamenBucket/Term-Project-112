from orderClockwise import orderClockwise
from clipping import clip
from intersectLine import *

def slicePoly(polyList, mousePoint1, mousePoint2, w, h):
    topPoly, bottomPoly = calculateSlicePolygons(mousePoint1, mousePoint2, w, h)
    poly1 = clip(polyList, topPoly)
    poly2 = clip(polyList, bottomPoly)
    return poly1, poly2

def calculateSlicePolygons(mousePoint1, mousePoint2, w, h):
    (x0,y0) = mousePoint1
    (x1,y1) = mousePoint2
    dx = x1 - x0
    dy = y1 - y0

    topPolygonList = []
    bottomPolygonList = []

    # if vertical slice
    if dx == 0:
        # adds intersections
        topPolygonList.append((x0,0))
        topPolygonList.append((x0,h))
        bottomPolygonList.append((x0,0))
        bottomPolygonList.append((x0,h))
        
        # adds corners
        topPolygonList.append((0,0))
        topPolygonList.append((0,h))
        bottomPolygonList.append((w,0))
        bottomPolygonList.append((w,h))
    # if horizontal slice
    elif dy == 0:
        # adds intersections
        topPolygonList.append((0,y0))
        topPolygonList.append((w,y0))
        bottomPolygonList.append((0,x0))
        bottomPolygonList.append((w,y0))

        # adds corners
        topPolygonList.append((0,0))
        topPolygonList.append((w,0))
        bottomPolygonList.append((0,h))
        bottomPolygonList.append((w,h))
    else:
        slope = (dy/dx)
        intercept = (y0) - (slope*x0)
        # adds intersections
        topPolygonList.extend(getIntercepts(slope,intercept,w,h))
        bottomPolygonList.extend(getIntercepts(slope,intercept,w,h))

        # checks the corners of the screen
        for xEnd,yEnd in [(0,0),(w,0),(w,h),(0,h)]:
            # check if the point is above line
            if yEnd > (slope*xEnd) + intercept:
                bottomPolygonList.append((xEnd,yEnd))
            else:
                topPolygonList.append((xEnd,yEnd))
    
    return orderClockwise(topPolygonList), orderClockwise(bottomPolygonList)

def getIntercepts(slope,intercept,width,height):
    # sides of the screen
    x0=0
    y0=0
    x1=width
    y1=height

    # points of intersection
    pt1 = (x0, slope*x0+intercept)
    pt2 = ((y0-intercept)/slope , y0)
    pt3 = (x1, slope*x1+intercept)
    pt4 = ((y1-intercept)/slope , y1)

    result = []
    # only takes point of interselction if it is on a side of the screen
    for x,y in [pt1,pt2,pt3,pt4]:
        if x>=0 and y>=0 and x<=width and y<=height:
            result.append((x,y))
    return result

def sliceIntersectsPolygon(polyList, mousePoint1, mousePoint2):
    x3,y3 = mousePoint1
    x4,y4 = mousePoint2
    p2 = Point(x3,y3)
    q2 = Point(x4,y4)
    for i in range(len(polyList)):
        point1 = polyList[i]
        point2 = polyList[(i+1)%len(polyList)]
        
        x1,y1 = point1
        x2,y2 = point2
        p1 = Point(x1,y1)
        q1 = Point(x2,y2)
        if doIntersect(p1,q1,p2,q2):
            return True
    return False

""" def testSliceIntersectsPolygon():
    polyList = [(50, 50), (462, 50), (462, 462), (50, 462)]
    mousePoint1, mousePoint2 = [(341, 14), (444, 15)]
    print(sliceIntersectsPolygon(polyList, mousePoint1, mousePoint2))
    polyList = [(50, 50), (462, 50), (462, 462), (50, 462)]
    mousePoint1, mousePoint2 = [(87, 23), (502, 345)]
    print(sliceIntersectsPolygon(polyList, mousePoint1, mousePoint2))

testSliceIntersectsPolygon() """