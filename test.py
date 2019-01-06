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
homedir="/home/pi/opc"

# INITIALIZATION
class menu:
	"""docstring for menu"""
	def __init__(self, name, menulist, funclist):
		super(menu, self).__init__()
		self.list = menulist
		self.parent = parent
		self.func = funclist
		self.name = name
		
	def getlist():
		return self.list

	def getfunc(pos):
		return self.func[pos]

	def getval(pos):
		return self.list[pos]

		
def init():

	serial = spi(device=0, port=0)
	device = sh1106(serial,rotate=2)
	drawText(device,['Initializing GPIO'])
	initgpio()
	#drawText(device,['Initializing GPIO',"Scanning Tapes"])
	#scanTapes(device)
	#drawText(device,['Initializing GPIO',"Scanning Tapes","Scanning Samples"])
	#scanSamples("dummy")
	#drawText(device,['Initializing GPIO',"Scanning Tapes","Scanning Samples","done."])

	#BOOTLOGO TEENAGE ENGINEERING

	#boot logo!
	#drawSplash(device)
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

def saveCaller(device, val):

	directory = homedir + "/projects/"
	projects = []

	for filename in os.listdir(directory):

		fullPath = directory + filename
		projects.append([filename,fullPath])

	projects.sort()

	save = menu("Save Project", ["NEW PROJECT"] ++ projects[:,0], [saveNew] ++ [overwrite]*len(projects))
	menuMove(device, menu)

def loadCaller(device, val):

	directory = homedir + "/projects/"
	projects = []

	for filename in os.listdir(directory):

		fullPath = directory + filename
		projects.append([filename,fullPath])

	projects.sort()

	load = menu("Load Project", projects[:,0], [load]*len(projects))
	menuMove(device, menu)

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
	width=128-2*xdist #width of hilight
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

		#if is_connected()==1:
		#	draw.rectangle((116,2,124,10), outline="black", fill="black")
		#else:
		#	draw.rectangle((116,2,124,10), outline="black", fill="white")

		# if GPIO.event_detected(lowBat):
		# 	draw.rectangle((96,3,108,9), outline="black", fill="black")
		# else:
		# 	draw.rectangle((96,3,108,9), outline="black", fill="white")




		draw.rectangle((xdist, (relative+1)*10+yoffset, xdist+width, ((relative+1)*10)+10+yoffset), outline="white", fill="white")
		
		for idx,line in enumerate(cutout):
			draw.text((xdist,(idx+1)*10+yoffset),line,mlistc[idx])


			#draw.rectangle((60,13,128,64), outline="black", fill="black")
			#draw.rectangle((60,13,61,48), outline="white", fill="white")

			#draw.rectangle((axdist, relative*10+yoffset, axdist+width, (relative*10)+10+yoffset), outline="white", fill="white")
		
			#for idx,line in enumerate(alist):
				#print("idx: ",idx,"line: ",line,"fill: ",flist[idx])
			#	draw.text((axdist,(idx+1)*10+yoffset),line,alistc[idx])

def menuMove(device, menu):
	pos = 0
	menulist = menu.getlist()
	menlen = len(menulist)
	dispListMenu(device, menu.name, menulist, pos)
	while True:
		if GPIO.event_detected(key['down']):
			pos = listMove(pos, 1, menlen)
			dispListMenu(device, menu.name, menulist, pos)
		elif GPIO.event_detected(key['up']):
			pos = listMove(pos, -1, menlen)
			dispListMenu(device, menu.name, menulist, pos)
		elif GPIO.event_detected(key['key1']):
			menu.getfunc(pos)(device, menu.getval(pos))
			dispListMenu(device, menu.name, menulist, pos)
		elif GPIO.event_detected(key['key3']):
			break



def main():
	device=init()
	main = menu("OP-1 Companion",["save project", "load project", "manage sample packs"], 
		[saveCaller, loadCaller, samplepackCaller])
	while True:
		menuMove(device, menu)

if __name__ == '__main__':
	main()
