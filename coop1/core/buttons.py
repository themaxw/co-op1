import RPi.GPIO as GPIO
from collections import deque
from typing import Callable

buttonId = {
    "key1": 21,
    "key2": 20,
    "key3": 16,
    "left": 5,
    "up": 6,
    "press": 13,
    "down": 19,
    "right": 26,
}


class ButtonFunctions:
    def __init__(self, buttonPress, moveStart, moveStop):
        self.buttonPress = buttonPress
        self.moveStart = moveStart
        self.moveStop = moveStop


class FunctionQueue:
    # TODO make threadsafe
    def __init__(self):
        self.q = deque()

    def put(self, elem: ButtonFunctions):
        self.q.append(elem)

    def peek(self) -> ButtonFunctions:
        if self.q:
            return self.q[-1]
        else:
            return None

    def pop(self) -> ButtonFunctions:
        return self.q.pop()

    def notEmpty(self) -> bool:
        if self.q:
            return True
        else:
            return False


class Buttons:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        for k in buttonId:
            GPIO.setup(buttonId[k], GPIO.IN, pull_up_down=GPIO.PUD_UP)

        for k in ["key1", "key2", "key3", "press"]:
            GPIO.add_event_detect(
                buttonId[k], GPIO.FALLING, callback=self.__press_button, bouncetime=300
            )

        for k in ["left", "down", "up", "right"]:
            GPIO.add_event_detect(
                buttonId[k], GPIO.BOTH, callback=self.__move, bouncetime=50
            )

        self.functions = FunctionQueue()

    def __press_button(self, key):

        if self.functions.notEmpty():
            self.functions.peek().buttonPress(key)

    def __move(self, key):

        if self.functions.notEmpty():
            if not GPIO.input(key):
                self.functions.peek().moveStart(key)
            else:
                self.functions.peek().moveStop(key)

    @staticmethod
    def __ignore_button(key):
        pass

    def putFunctions(
        self,
        onButtonPress: Callable = None,
        onMoveStart: Callable = None,
        onMoveStop: Callable = None,
    ):
        if not onButtonPress:
            onButtonPress = self.__ignore_button

        if not onMoveStart:
            onMoveStart = self.__ignore_button

        if not onMoveStop:
            onMoveStop = self.__ignore_button

        self.functions.put(ButtonFunctions(onButtonPress, onMoveStart, onMoveStop))

    def removeFunctions(self):
        self.functions.pop()
