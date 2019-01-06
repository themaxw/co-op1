from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import sh1106
import time,os,datetime
import RPi.GPIO as GPIO
import shutil as sh
import usb.core
from subprocess import *

#GLOBALS

#KEYS
key={}
key['key1']=5 #broken on menona
key['key2']=20
key['key3']=16

key['left']=5 
key['up']=6
key['press']=13
key['down']=19
key['right']=26


#lowBat=4

VENDOR = 0x2367
PRODUCT = 0x0002
MOUNT_DIR = "/media/op1"
USBID_OP1 = "*Teenage_OP-1*"

op1path=MOUNT_DIR
homedir="/home/pi/opc"#

# INITIALIZATION

def init():

	serial = spi(device=0, port=0)
	device = sh1106(serial,rotate=2)
	drawText(device,['Initializing GPIO'])
	initgpio()
	drawText(device,['Initializing GPIO',"Scanning Tapes"])
	scanTapes(device)
	drawText(device,['Initializing GPIO',"Scanning Tapes","Scanning Samples"])
	scanSamples("dummy")
	drawText(device,['Initializing GPIO',"Scanning Tapes","Scanning Samples","done."])

	#boot logo!
	drawSplash(device)
	time.sleep(2)




	return device

def initgpio():

	print("Initializing GPIO")
	#Initialize GPIO
	GPIO.setmode(GPIO.BCM)
	

	GPIO.setup(key['key1'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(key['key2'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(key['key3'], GPIO.IN, pull_up_down=GPIO.PUD_UP)

	GPIO.setup(key['left'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(key['up'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(key['press'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(key['down'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(key['right'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
	
	#LIPO LOW BATTERY
	#GPIO.setup(lowBat, GPIO.IN,pull_up_down=GPIO.PUD_UP)

	GPIO.add_event_detect(key['key1'], GPIO.FALLING,bouncetime=300)
	GPIO.add_event_detect(key['key2'], GPIO.FALLING,bouncetime=300)
	GPIO.add_event_detect(key['key3'], GPIO.FALLING,bouncetime=300)
	GPIO.add_event_detect(key['left'], GPIO.FALLING,bouncetime=300)
	GPIO.add_event_detect(key['up'], GPIO.FALLING,bouncetime=300)
	GPIO.add_event_detect(key['press'], GPIO.FALLING,bouncetime=300)
	GPIO.add_event_detect(key['down'], GPIO.FALLING,bouncetime=300)
	GPIO.add_event_detect(key['right'], GPIO.FALLING,bouncetime=300)

def drawText(device,textlist):
	with canvas(device) as draw:
		for idx,text in enumerate(textlist):
			#print text, ", ", idx
			draw.text((0,idx*10),text,"white")

def main():
	device=init()
	while True:
		if GPIO.event_detected(key['key2']):
			drawText(device,["helo"])

if __name__ == '__main__':
	main()