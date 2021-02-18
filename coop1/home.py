from coop1.core.device import Menu, Device
import RPi.GPIO as GPIO
from coop1.programs.fileBrowser import fileBrowser
from coop1.programs.opc import opc, is_connected
from coop1.programs.settings import settings
from time import sleep


def nothing(device, val):
    pass


def test():
    return True


def main():
    device = Device([is_connected, test])
    device.dispImage("/home/pi/opc/resources/coOP_logo.bmp")
    homeMenu = Menu(
        "Home",
        [
            ("Files", fileBrowser),
            ("opc", opc),
            ("audioplayer", nothing),
            ("settings", settings),
            ("reboot", nothing),
        ],
    )
    sleep(2)

    try:
        while True:
            device.dispMenu(homeMenu)
            sleep(0.01)
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("bye have a nice day")


if __name__ == "__main__":
    main()
