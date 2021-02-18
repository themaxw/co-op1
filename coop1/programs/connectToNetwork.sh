#!/bin/bash
python3 - << EOF
from wifi import Cell, Scheme
import pickle

with open('/home/pi/opc/network.pkl', 'rb') as f:
	scheme = pickle.load(f)
scheme.save()
scheme.activate()

EOF
