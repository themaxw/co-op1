from coop1.core.device import Menu, Device
import RPi.GPIO as GPIO
from coop1.programs.fileBrowser import fileBrowser
from coop1.programs.opc import opc, is_connected
from coop1.programs.settings import settings

from coop1.core.screen import Device
from coop1.core.statusFunctions import is_connected, wifi_status
from coop1.core.programManager import ProgramManager
from coop1.core.listmenu import Listmenu, listItemBase, menuItem, commandItem
from time import sleep
import signal


def nothing(device, val):
    pass


def test():
    return True


def main():
    device = Device([is_connected, wifi_status], 9)
    secondMenu = Listmenu(
        "SubMenu", [listItemBase(str(x)) for x in range(4, 15)], device
    )

    mainMenu = Listmenu(
        "Home",
        [
            menuItem("submenu", secondMenu),
            listItemBase("2"),
            listItemBase("3"),
            commandItem("shutdown", "sudo shutdown -h now"),
        ],
        device,
    )

    programManager = ProgramManager(mainMenu)

    def handleTerminationSignal(signalNumber, frame):
        print("shutting down")
        programManager.killMe.set()
        device.stop()

    signal.signal(signal.SIGTERM, handleTerminationSignal)
    signal.signal(signal.SIGINT, handleTerminationSignal)


# def main():
#     device = Device([is_connected, test])
#     device.dispImage("/home/pi/opc/resources/coOP_logo.bmp")
#     homeMenu = Menu(
#         "Home",
#         [
#             ("Files", fileBrowser),
#             ("opc", opc),
#             ("audioplayer", nothing),
#             ("settings", settings),
#             ("reboot", nothing),
#         ],
#     )
#     sleep(2)

#     try:
#         while True:
#             device.dispMenu(homeMenu)
#             sleep(0.01)
#     except KeyboardInterrupt:
#         GPIO.cleanup()
#         print("bye have a nice day")


if __name__ == "__main__":
    main()
