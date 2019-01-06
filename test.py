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
key['key1']=21 #broken on menona
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

def listMove(pos, step, size):
	return (pos+step)%size

def drawText(device,textlist):
	with canvas(device) as draw:
		for idx,text in enumerate(textlist):
			#print text, ", ", idx
			draw.text((0,idx*10),text,"white")

def dispListMenu(device,title,menu,pos):
	menlen = len(menu)
	if menlen>5:
		if pos == 0 or pos == 1:
			cutout = menu[:5]
			relative = pos
		elif pos == menlen-1 or pos == menlen-2:
			cutout = menu[-5: ]
			relative = 4-(menlen-1-pos)
		else:
			cutout = menu[pos-2:pos+3]
			relative = 2
	else:
		cutout = menu
		relative = pos 


	#offsets
	xdist=5 #x offset
	yoffset=4
	
	#menu
	width=100 #width of hilight
	mlistc=["white"]*len(cutout)
	mlistc[relative] = "black"

	#action menu
	#axdist=64
	#alist=["action1", "action2","action3"]
	#alistc=["white"]*len(alist)
	#if apos != 0:
	#	alistc[apos-1]="black"



	with canvas(device) as draw:

		#draw title
		draw.rectangle((0,0,128,12), outline="white", fill="white")
		#draw.rectangle((1,10,126,11), outline="black", fill="black")
		draw.text((2,0),title,"black")

		# // STATUS BAR //

		if is_connected()==1:
			draw.rectangle((116,2,124,10), outline="black", fill="black")
		else:
			draw.rectangle((116,2,124,10), outline="black", fill="white")

		# if GPIO.event_detected(lowBat):
		# 	draw.rectangle((96,3,108,9), outline="black", fill="black")
		# else:
		# 	draw.rectangle((96,3,108,9), outline="black", fill="white")




		draw.rectangle((xdist, pos*10+yoffset, xdist+width, (pos*10)+10+yoffset), outline="white", fill="white")
		
		for idx,line in enumerate(cutout):
			draw.text((xdist,(idx+1)*10+yoffset),line,mlistc[idx])


			#draw.rectangle((60,13,128,64), outline="black", fill="black")
			#draw.rectangle((60,13,61,48), outline="white", fill="white")

			#draw.rectangle((axdist, relative*10+yoffset, axdist+width, (relative*10)+10+yoffset), outline="white", fill="white")
		
			#for idx,line in enumerate(alist):
				#print("idx: ",idx,"line: ",line,"fill: ",flist[idx])
			#	draw.text((axdist,(idx+1)*10+yoffset),line,alistc[idx])

def menuMove(device, menu, name):
	pos = 0
	menlen = len(menu)
	dispListMenu(device, name, menu, pos)
	while True:
		if GPIO.event_detected(key['down']):
			pos = listMove(pos, 1, menlen)
			dispListMenu(device, name, menu, pos)
		elif GPIO.event_detected(key['up']):
			pos = listMove(pos, -1, menlen)
			dispListMenu(device, name, menu, pos)

def main():
	device=init()
	menu = ["save project", "load project", "manage sample packs"]
	menuMove(device, menu, "OP-1 Companion")

if __name__ == '__main__':
	main()