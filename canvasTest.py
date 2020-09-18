from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import sh1106
import time,os,datetime
from subprocess import *
import RPi.GPIO as GPIO
from time import sleep
from PIL import Image, ImageDraw

from random import randint, random

serial = spi(device=0, port=0)
device = sh1106(serial,rotate=2)

def clip(n, minn, maxn):
    return n
    return max(min(maxn, n), minn)

def randCoords(xy, spread):
    x = xy[0]
    y = xy[1]
    xlower = clip(x-spread, 0, 127)
    xupper = clip(x+spread, 0, 127)
    ylower = clip(y-spread, 0, 63)
    yupper = clip(y+spread, 0, 63)
    x = randint(xlower, xupper)
    y = randint(ylower, yupper)
    return (x, y)

def randomizeCoordList(coords):
    coords = [randCoords(xy, 3) for xy in coords]

# coords = [(63,31)] * 20
# while True:
#     with canvas(device) as draw:

#         draw.polygon(coords, outline="white")
#         coords = [randCoords(xy, 5) for xy in coords]
#     sleep(0.01)

im = Image.new("RGBA", (128,64))
i = ImageDraw.Draw(im)
i.polygon([(1,1), (30,50), (125,63)], outline="white")
with canvas(device) as draw:
    draw.bitmap((0,0), im, fill="white")
print("ayyy")
sleep(10)

