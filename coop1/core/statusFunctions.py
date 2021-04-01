import usb.core
from wifi import Cell, Scheme
from PIL import Image
from PIL.ImageOps import invert
from os import path
from pathlib import Path


VENDOR = 0x2367
PRODUCT = 0x0002
resourcePath = Path(__file__).parent.parent
resourcePath = resourcePath.joinpath("resources")


def loadStatusIcon(filename):
    img = Image.open(resourcePath / filename)
    return invert(img.convert("RGB")).convert("1")


_op1_connected = loadStatusIcon("op1_connected.xbm")
_op1_notConnected = loadStatusIcon("op1_notConnected.xbm")

_wifi_notConnected = loadStatusIcon("wifi_notConnected.xbm")
_wifi_25 = loadStatusIcon("wifi_25.xbm")
_wifi_50 = loadStatusIcon("wifi_50.xbm")
_wifi_75 = loadStatusIcon("wifi_75.xbm")
_wifi_100 = loadStatusIcon("wifi_100.xbm")


def is_connected():
    if usb.core.find(idVendor=VENDOR, idProduct=PRODUCT) is not None:
        return _op1_connected
    else:
        return _op1_notConnected
        # return not connected img


def wifi_status():
    # TODO get signal strength/connection status EFFICIENTLY (or cache it and only check every 5 seconds or so)
    signal = 0.5
    if signal is None:
        return _wifi_notConnected
    elif signal <= 0.25:
        return _wifi_25
    elif signal <= 0.50:
        return _wifi_50
    elif signal <= 0.75:
        return _wifi_75
    else:
        return _wifi_100