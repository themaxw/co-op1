from coop1.core.device import Device, Menu
from wifi import Cell, Scheme
import pickle
from subprocess import Popen, PIPE, call
from typing import List


def scanNetworks() -> List[Cell]:
    p = call(["sudo", "/home/pi/opc/getNetworksPython.sh"])
    with open("/home/pi/opc/wifi.pkl", "rb") as f:
        n = pickle.load(f)
    return n


def connectToNetwork(device: Device, val, args):
    cell = args[0]
    if cell.encrypted:
        device.dispError(["Enter Password"])
        password = device.dispKeyboard()
    else:
        password = None

    scheme = Scheme.for_cell("wlan0", cell.ssid, cell, password)
    with open("/home/pi/opc/network.pkl", "wb") as f:
        pickle.dump(scheme, f)
    p = call(["sudo", "/home/pi/opc/connectToNetwork.sh"])


def wifiConnect(device: Device, val):
    networks = scanNetworks()
    networkList = [(c.ssid, connectToNetwork, [c]) for c in networks]
    menu = Menu("Connect to Network", networkList, True)
    device.dispMenu(menu)


def wifiSettings(device: Device, val):
    menu = Menu(
        "Wi-Fi",
        [
            ("connect to new network", wifiConnect),
            ("connect to saved network", nothing),
        ],
    )
    device.dispMenu(menu)


def settings(device: Device, val):
    menu = Menu("Settings", [("Wi-Fi", wifiSettings), ("Bluetooth", nothing)])
    device.dispMenu(menu)


def nothing(device, val):
    pass


if __name__ == "__main__":
    d = Device()
    wifiSettings(d, None)