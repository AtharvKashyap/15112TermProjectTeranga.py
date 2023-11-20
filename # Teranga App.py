# Teranga App
from cmu_graphics import *

def onAppStart(app):
    pass

def drawHome(app):
    drawRect(0,0,1920,1080,fill=rgb(255, 223, 121))
    drawRect(0,370,1920,630,fill=rgb(251, 112, 65))
    drawRect(320,300,900,800,fill='white')
    drawRect(0,0,1920,80,fill='white')

def redrawAll(app):
    drawHome(app)

def main():
    runApp(1920, 1080)

main()