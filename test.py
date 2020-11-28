from cmu_112_graphics import *
from boid import Boid

def appStarted(app):
    app.flock = []
    initFlock(app)

def initFlock(app):
    amount = 10
    for i in range(amount):
        pos = [app.width/2, app.height/2]
        vel = [0, 0]
        acc = [0, 0]
        app.flock.append(Boid(pos, vel, acc))

def redrawAll(app, canvas):
    for boid in app.flock:
        boid.show(app, canvas)
    

runApp(width=512, height=512)
