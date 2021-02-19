from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import sh1106
import RPi.GPIO as GPIO
from time import sleep, time
from PIL import Image, ImageDraw
from threading import Timer, Event
from queue import Queue
from pathlib import Path

from coop1.core.buttons import Buttons


class Frame:
    def __init__(self, frame, fullscreen):
        self.fr = frame
        self.fullscreen = fullscreen


XDIM = 128
YDIM = 64


class Device:
    def __init__(self, statusFunctions=[], framerate: int = 10):

        serial = spi(device=0, port=0)
        self.device = sh1106(serial, rotate=2)

        self.buttons = Buttons()

        if statusFunctions is None:
            statusFunctions = []
        self.statusFunctions = statusFunctions
        self.stopEvent = Event()
        self.frameBuffer = Queue()

        resourcePath = Path(__file__).parent.parent
        resourcePath = resourcePath.joinpath("resources")
        im = Image.open(resourcePath / "coOP_logo.bmp").convert(self.device.mode)

        self.frameBuffer.put(Frame(im, True))
        self.lastFrame = None

        self.fullscreenOffset = 10

        self.timeToNextFrame = 1 / framerate

        self.__updateScreen()
        # print logo to device

    def __updateScreen(self):
        # TODO this is really inefficient
        start = time()

        background = Image.new(self.device.mode, self.device.size)

        # Get New Frame
        if self.frameBuffer.empty():
            f = self.lastFrame
            newFrame = False
        else:
            f = self.frameBuffer.get()
            self.lastFrame = f
            newFrame = True
        t1 = time()

        if f.fullscreen:
            background.paste(f.fr, (0, 0))

        else:
            titlebar = Image.new(
                self.device.mode, (XDIM, self.fullscreenOffset), color="white"
            )
            background.paste(f.fr, (0, self.fullscreenOffset))
            background.paste(titlebar, (0, 0))
            for i, status in enumerate(self.statusFunctions):
                background.paste(status(), (XDIM - 1 - 10 * (i + 1), 0))

        t2 = time()
        self.device.display(background)

        end = time()
        if end - start > self.timeToNextFrame:
            print(
                "update length {}/{} with {}".format(
                    end - start,
                    self.timeToNextFrame,
                    "new frame" if newFrame else "reused frame",
                )
            )
            print("flushing to screen: {}, drawing: {}".format(end - t2, t2 - t1))

        # setup next call to __updateScreen

        if not self.stopEvent.isSet():
            timeToNextFrame = self.timeToNextFrame - (end - start)
            if timeToNextFrame < 0:
                timeToNextFrame = 0.001
            Timer(self.timeToNextFrame, self.__updateScreen).start()

    def stop(self):
        self.stopEvent.set()

    def addFrames(self, frames, fullscreen=True):
        for f in frames:
            newFrame = Frame(f, fullscreen)
            self.frameBuffer.put(newFrame)

    def baseFrame(self, fullscreen=True):
        if fullscreen:
            f = Image.new(self.device.mode, (XDIM, YDIM))
        else:
            f = Image.new(self.device.mode, (XDIM, YDIM - self.fullscreenOffset))

        drawFrame = ImageDraw.Draw(f)
        return f, drawFrame


if __name__ == "__main__":
    from statusFunctions import is_connected, wifi_status

    scr = Device([is_connected, wifi_status], 10)
    sleep(1)
    f, draw = scr.baseFrame(fullscreen=False)
    draw.polygon([(20, 10), (34, 40), (127, 54)], outline="white")
    scr.addFrames([f], fullscreen=False)
    # newFrames = []
    # for i in range(10):
    #     f, draw = Device.baseFrame()
    #     corners = [(64-10*i, 32-5*i),(64+10*i, 32-5*i),(64+10*i, 32+5*i),(64-10*i, 32+5*i)]
    #     draw.polygon(corners, outline="white")
    #     newFrames.append(f)
    # scr.addFrames(newFrames*5)

    sleep(10)
    scr.stop()