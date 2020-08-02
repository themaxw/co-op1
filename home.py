from device import Menu, Device
import RPi.GPIO as GPIO
from fileBrowser import fileBrowser
from opc import opc, is_connected
from config import settings
from time import sleep

def nothing(device, val):
    pass

def test():
    return True



def main():
    device = Device([is_connected, test])
    device.dispImage("coOP_logo.bmp")  
    homeMenu = Menu("Home", [("Files", fileBrowser), ("opc", opc), ("audioplayer", nothing), ("settings", settings), ("reboot", nothing)])
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