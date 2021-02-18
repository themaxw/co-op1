from bluetoothctl import Bluetoothctl
import bluetooth

def scan():
    devices = bluetooth.discover_devices(lookup_names=True, lookup_class=True)
    return devices

def connect(mac):
    b = Bluetoothctl()
    b.send(command="agent on")
    b.send(command="default-agent")
    #TODO trust und pair
    b.connect(mac)

    
