from cmu_112_graphics import *

class TestClass(object):
    def __init__(self, text):
        self.text = text

    def displayText(self, app, canvas):
        canvas.create_text(app.width/2, app.height/2, text = self.text)


def appStarted(app):
    app.test = TestClass("hello")

def redrawAll(app, canvas):
    app.test.displayText(app, canvas)

runApp(width=256, height=256)
