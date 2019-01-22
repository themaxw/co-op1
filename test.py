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

keypressed = {}
keypressed[key['left']] = False
keypressed[key['up']] = False
keypressed[key['down']] = False
keypressed[key['right']] = False

keybounce = {}

keybounce[key['left']] = 0
keybounce[key['up']] = 0
keybounce[key['down']] = 0
keybounce[key['right']] = 0


keyboard = [['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['q', 'w', 'e', 'r', 't', 'z', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', '_'],
            ['y', 'x', 'c', 'v', 'b', 'n', 'm', '-', '(', ')']]
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
        #super(menu, self).__init__()
        self.list = menulist
        self.func = funclist
        self.name = name
        
    def getlist(self):
        return self.list

    def getfunc(self, pos):
        return self.func[pos]

    def getval(self, pos):
        return self.list[pos]

        
def init():

    serial = spi(device=0, port=0)
    device = sh1106(serial,rotate=2)
    drawText(device,['Initializing GPIO'])
    initgpio()
    initFile()
    #drawText(device,['Initializing GPIO',"Scanning Tapes"])
    #scanTapes(device)
    #drawText(device,['Initializing GPIO',"Scanning Tapes","Scanning Samples"])
    #scanSamples("dummy")
    #drawText(device,['Initializing GPIO',"Scanning Tapes","Scanning Samples","done."])

    #BOOTLOGO TEENAGE ENGINEERING

    #boot logo!
    #drawSplash(device)
    #time.sleep(2)

    return device

def initFile():
    mkdir(homedir + "/projects/")
    mkdir(homedir + "/samplepacks/")
    mkdir(MOUNT_DIR)

def initgpio():

    print("Initializing GPIO")
    #Initialize GPIO
    #GPIO.cleanup()
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
    GPIO.add_event_detect(key['press'], GPIO.FALLING,bouncetime=300)
    
    GPIO.add_event_detect(key['left'], GPIO.BOTH,callback=move, bouncetime=50)
    GPIO.add_event_detect(key['up'], GPIO.BOTH,callback=move, bouncetime=50)
    GPIO.add_event_detect(key['down'], GPIO.BOTH,callback=move, bouncetime=50)
    GPIO.add_event_detect(key['right'], GPIO.BOTH,callback=move, bouncetime=50)

###shoutouts to tink3rtanker
## do not work tho
def is_connected():
    return usb.core.find(idVendor=VENDOR, idProduct=PRODUCT) is not None

def getmountpath():
    o = os.popen('readlink -f /dev/disk/by-id/' + USBID_OP1).read()
    if USBID_OP1 in o:
        return False
    else:
        return o.rstrip()

def mountdevice():
    source = getmountpath()
    target = MOUNT_DIR
    if target is False:
        return False

    ret = os.system('sudo mount {} {}'.format(source, target))
    if ret not in (0, 8192):
        return False
    return True


def unmountdevice():
    target = MOUNT_DIR
    ret = os.system('sudo umount {}'.format(target))
    if ret != 0:
        return False
    return True

####

def move(key):
    if GPIO.input(key) == 0:
        keypressed[key] = True
        keybounce[key] = time.clock()
    else:
        keypressed[key] = False

def isPressed(key, bouncetime=0.1):
    if keypressed[key] and time.clock()-keybounce[key] >= bouncetime:
        keybounce[key] = time.clock()
        return True
    else:
        return False
def dispError(device, text):
    with canvas(device) as draw:

        #center this plz
        draw.rectangle((8,8,120,56), outline="black", fill="white")
        draw.rectangle((10,10,118,54), outline="white", fill="black")
        for i, line in enumerate(text):
            if len(line)>19:
                line = line[:19]

            draw.text((64-int(len(line)*2.5), 15 + 15*i),line,"white")
    time.sleep(1)
        
def copy_and_overwrite(from_path, to_path):
    #if os.path.exists(to_path):
    #    os.system("sudo rm "+ to_path)
    os.system("sudo cp " + from_path + " " + to_path)

def listMove(pos, step, size):
    return (pos+step)%size

def drawText(device,textlist):
    with canvas(device) as draw:
        for idx,text in enumerate(textlist):
            draw.text((0,idx*10),text,"white")

def drawProgress(device,title,progress):
    with canvas(device) as draw:
        progpix=progress*64
        draw.text((16,8),title,"white")
        draw.rectangle((32,32,96,42), outline="white", fill="black")
        draw.rectangle((32,32,32+progpix,42), outline="white", fill="white")

def dispListMenu(device,title,menu,pos):
    #choose cutout to show
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
    #   alistc[apos-1]="black"



    with canvas(device) as draw:

        #draw title
        draw.rectangle((0,0,128,12), outline="white", fill="white")
        #draw.rectangle((1,10,126,11), outline="black", fill="black")
        draw.text((2,0),title,"black")

        # // STATUS BAR //
        #create better icons
        if is_connected()==1:
            draw.rectangle((116,2,124,10), outline="black", fill="black")
        else:
            draw.rectangle((116,2,124,10), outline="black", fill="white")

        # if GPIO.event_detected(lowBat):
        #   draw.rectangle((96,3,108,9), outline="black", fill="black")
        # else:
        #   draw.rectangle((96,3,108,9), outline="black", fill="white")




        draw.rectangle((xdist, (relative+1)*10+yoffset, xdist+width, ((relative+1)*10)+10+yoffset), outline="white", fill="white")
        
        for idx,line in enumerate(cutout):
            draw.text((xdist,(idx+1)*10+yoffset),line,mlistc[idx])


            #draw.rectangle((60,13,128,64), outline="black", fill="black")
            #draw.rectangle((60,13,61,48), outline="white", fill="white")

            #draw.rectangle((axdist, relative*10+yoffset, axdist+width, (relative*10)+10+yoffset), outline="white", fill="white")
        
            #for idx,line in enumerate(alist):
                #print("idx: ",idx,"line: ",line,"fill: ",flist[idx])
            #   draw.text((axdist,(idx+1)*10+yoffset),line,alistc[idx])


def menuMove(device, menu, mode=0):
    """default mode 0, mode 1 returns val"""

    pos = 0
    menulist = menu.getlist()
    menlen = len(menulist)
    dispListMenu(device, menu.name, menulist, pos)
    while True:

        if isPressed(key['down']):
            pos = listMove(pos, 1, menlen)
            dispListMenu(device, menu.name, menulist, pos)

        elif isPressed(key['up']):
            pos = listMove(pos, -1, menlen)
            dispListMenu(device, menu.name, menulist, pos)

        elif GPIO.event_detected(key['key1']):
            if mode == 0:
                exit = menu.getfunc(pos)(device, menu.getval(pos))
                if exit:
                    break

            elif mode == 1:
                return menu.getval(pos)
            else:
                break

            dispListMenu(device, menu.name, menulist, pos)

        elif GPIO.event_detected(key['key3']):
            break

def mkdir(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def drawKeyboard(device, word, position):
    with canvas(device) as draw:
        draw.text((10, 5), word, "white")
        ioff = 20
        joff = 14
        iofft = 0
        jofft = 3
        for i, row in enumerate(keyboard):
            for j, field in enumerate(row):
                if (i, j) == position:
                    draw.rectangle((joff+j*10, ioff+i*10, joff+j*10+10, ioff+i*10+10), outline="white", fill="white")
                    draw.text((joff+j*10+jofft, ioff+i*10+iofft), field, "black")
                else:
                    draw.text((joff+j*10+jofft, ioff+i*10+iofft), field, "white")


#enter a name
def enterName(device, path=None):
    """opens a keyboard, returns entered word, if you don't want duplicate checking don't supply a path"""
    name = ""
    i = 0
    j = 0
    drawKeyboard(device, name, (i, j))
    while True:
        if isPressed(key['down'], 0.075):
            i = listMove(i, 1, 4)
            drawKeyboard(device, name, (i, j))

        elif isPressed(key['up'], 0.075):
            i = listMove(i, -1, 4)
            drawKeyboard(device, name, (i, j))

        elif isPressed(key['left'], 0.075):
            j = listMove(j, -1, 10)
            drawKeyboard(device, name, (i, j))

        elif isPressed(key['right'], 0.075):
            j = listMove(j, 1, 10)
            drawKeyboard(device, name, (i, j))

        elif GPIO.event_detected(key['press']):
            if len(name)<19:
                name = name + keyboard[i][j]
                drawKeyboard(device, name, (i, j))

        elif GPIO.event_detected(key['key1']):
            if name != "":
                name = name [:-1]
            drawKeyboard(device, name, (i, j))

        elif GPIO.event_detected(key['key2']):
            return ""

        elif GPIO.event_detected(key['key3']):
            if path is not None and os.path.isdir(path + name):
                dispError(device, ["name schon", "vergeben"])
            else:
                return name

def saveNew(device, val):
    if is_connected():
        name = enterName(device, homedir + "/projects/")
        if name == "":
            return False

        newdir = homedir+ "/projects/"+name+"/"
        #mkdir(newdir)

        mounted = mountdevice()
        if not mounted:
            dispError(device, ["Dear OP-1,", "Where Art Thou"])
            return False

        drawProgress(device, "saving Tape...", 0)
        sh.copytree("/media/op1/tape", newdir+"tape")

        drawProgress(device, "saving Synth...", 0.6)
        sh.copytree("/media/op1/synth/user", newdir+"synth/user")

        drawProgress(device, "saving Drums...", 0.8)
        sh.copytree("/media/op1/drum/user", newdir+"drum/user")


        print("copy abgeschlossen")

        unmounted = unmountdevice()
        if not unmounted:
            dispError(device, ["unmount failed", "RIP in Pepperoni"])
            return False

        drawProgress(device, "successfully saved", 1)
        time.sleep(0.5)
        return True
    else:
        dispError(device, ["404", "OP-1 not found"])
        return False



def overwrite(device, project):
    #prompt full save/ARE YOU SURE ABOUT THAT?
    prompt = menu("Are you sure about that?", ["yes", "no"], [nothing, nothing])
    sure = menuMove(device, prompt, 1)
    
    if sure == "no":
        return False

    if is_connected():

        savdir = homedir+ "/projects/"+project+"/"
        #mkdir(newdir)

        mounted = mountdevice()
        if not mounted:
            dispError(device, ["Dear OP-1,", "Where Art Thou"])
            return False

        # drawProgress(device, "saving Tape...", 0)
        # copy_and_overwrite("/media/op1/tape", savdir+"tape")

        # drawProgress(device, "saving Synth...", 0.6)
        # copy_and_overwrite("/media/op1/synth/user", savdir+"synth/user")

        # drawProgress(device, "saving Drums...", 0.8)
        # copy_and_overwrite("/media/op1/drum/user", savdir+"drum/user")
        drawProgress(device, "saving Tape...", 0)
        for i, tape in enumerate(os.listdir( "/media/op1/tape/")):
            copy_and_overwrite( "/media/op1/tape/"+tape, savdir+"tape/"+tape)
            drawProgress(device, "saving Tape...", 0.2*i)

        drawProgress(device, "saving Synth...", 0.8)
        for i, synth in enumerate(os.listdir("/media/op1/synth/user/")):
            copy_and_overwrite("/media/op1/synth/user/"+synth, savdir+"synth/user/"+synth)

        drawProgress(device, "saving Drums...", 0.9)
        for i, drum in enumerate(os.listdir("/media/op1/drum/user/")):
            copy_and_overwrite("/media/op1/drum/user/"+drum, savdir+"drum/user/"+drum)


        print("copy abgeschlossen")

        unmounted = unmountdevice()
        if not unmounted :
            dispError(device, ["unmount failed", "RIP in Pepperoni"])
            return False

        drawProgress(device, "successfully saved", 1)
        time.sleep(0.5)
        return True
    else:
        dispError(device, ["404", "OP-1 not found"])
        return False

def load(device, project):
    prompt = menu("Are you sure about that?", ["yes", "no"], [nothing, nothing])
    sure = menuMove(device, prompt, 1)
    if sure == "no":
        return False

    if is_connected():

        loaddir = homedir+ "/projects/"+project+"/"
        #mkdir(newdir)

        mounted = mountdevice()
        if not mounted:
            dispError(device, ["Dear OP-1,", "Where Art Thou"])
            return False

        drawProgress(device, "loading Tape...", 0)
        for i, tape in enumerate(os.listdir(loaddir+"tape/")):
            copy_and_overwrite(loaddir+"tape/"+tape, "/media/op1/tape/"+tape)
            drawProgress(device, "loading Tape...", 0.2*i)

        # drawProgress(device, "loading Synth...", 0.8)
        # for i, synth in enumerate(os.listdir(loaddir+"synth/user/")):
        #     copy_and_overwrite(loaddir+"synth/user/"+synth, "/media/op1/synth/user/"+synth)

        # drawProgress(device, "loading Drums...", 0.9)
        # for i, drum in enumerate(os.listdir(loaddir+"drum/user/")):
        #     copy_and_overwrite(loaddir+"drum/user/"+drum, "/media/op1/drum/user/"+drum)


        print("load abgeschlossen")

        unmounted = unmountdevice()
        if not unmounted:
            dispError(device, ["unmount failed", "RIP in Pepperoni"])
            return False

        drawProgress(device, "successfully loaded", 1)
        time.sleep(0.5)
        return True
    else:
        dispError(device, ["404", " OP-1 not found"])
        return False

def nothing(device, val):
    pass

def saveCaller(device, val):

    directory = homedir + "/projects/"
    projects = []

    for filename in os.listdir(directory):

        fullPath = directory + filename
        projects.append(filename)

    projects.sort()

    save = menu("Save Project", ["NEW PROJECT"] + projects, [saveNew] + [overwrite]*len(projects))
    menuMove(device, save)

def loadCaller(device, val):

    directory = homedir + "/projects/"
    projects = []

    for filename in os.listdir(directory):

        fullPath = directory + filename
        projects.append(filename)

    projects.sort()
    if len(projects) == 0:
        projects.append("no projects found")
        actions = [nothing]
    else:
        actions = [load]*len(projects)

    print(projects)
    loadM = menu("Load Project", projects, actions)
    menuMove(device, loadM)

def samplepackCaller(device, val):

    directory = homedir + "/samplepacks/"
    samplepacks = []

    for filename in os.listdir(directory):

        fullPath = directory + filename
        samplepacks.append(filename)

    samplepacks.sort()
    if len(samplepacks) == 0:
        samplepacks.append("no samplepacks found")
        actions = [nothing]
    else:
        actions = [load]*len(samplepacks)
        
    samples = menu("Samplepacks", samplepacks, actions)
    menuMove(device, samples)


    
def restart(device, val):
    os.system("sudo reboot")

if __name__ == '__main__':
    device = init()
    main = menu("OP-1 Companion",["save project", "load project", "export song", "manage sample packs", "restart"], [saveCaller, loadCaller, nothing, samplepackCaller, restart])
    try:
        while True:
            menuMove(device, main)
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("bye, have a nice day")
