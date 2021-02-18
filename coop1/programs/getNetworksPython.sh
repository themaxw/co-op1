#!/bin/bash
python3 - << EOF
from wifi import Cell, Scheme
import pickle
networks = list(Cell.all('wlan0'))
print([(c.ssid, c.quality, c.encrypted) for c in networks])

with open('/home/pi/opc/wifi.pkl', 'wb') as f:
	pickle.dump(networks, f)

EOF
