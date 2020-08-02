from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import sh1106
import time,os,datetime
from subprocess import *
import RPi.GPIO as GPIO
from time import sleep
from PIL import Image

from typing import Iterable, Tuple, Callable, List, Optional, Any

key={
    'key1': 21, 
    'key2': 20, 
    'key3': 16, 
    'left': 5,
    'up': 6, 
    'press': 13, 
    'down': 19, 
    'right': 26
}

class Menu:
    
    #Item = Tuple[str, Callable[[Device, str, Optional[List[Any]]], None]]
    def __init__(self, name: str, itemList, hasargs = False):
        """Constructor for class Menu
        
        Arguments:
            name {str} -- Name of the Menu
            itemList {List[Tuple]} -- List of Tuples containing items and their corresponding functions
        """
        self.list = []
        self.func = []
        self.args = []

        self.hasargs = hasargs
        
        if self.hasargs:
            for itemName, itemFunc, itemArgs in itemList:
                self.list.append(itemName)
                self.func.append(itemFunc)
                self.args.append(itemArgs)
        else:
            for itemName, itemFunc in itemList:
                self.list.append(itemName)
                self.func.append(itemFunc)
                
        self.name = name
        

    def getlist(self):
        return self.list

    def getfunc(self, pos):
        return self.func[pos]

    def getval(self, pos):
        return self.list[pos]

    def getargs(self, pos):
        return self.args[pos]


class Device:
    key={
        'key1': 21, 
        'key2': 20, 
        'key3': 16, 
        'left': 5,
        'up': 6, 
        'press': 13, 
        'down': 19, 
        'right': 26
    }

    keypressed = {
        key['left']: False,
        key['up']: False,
        key['down']: False,
        key['right']: False
    }

    keybounce = {
        key['left']: 0,
        key['up']: 0,
        key['down']: 0,
        key['right']: 0
    }

    #TODO more keys, shift key etc
    keyboard = [['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                ['q', 'w', 'e', 'r', 't', 'z', 'u', 'i', 'o', 'p'],
                ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', '_'],
                ['y', 'x', 'c', 'v', 'b', 'n', 'm', '-', '(', ')']]

    def __init__(self, statusFunctions: Optional[List[Callable[[], bool]]] = []):

        if statusFunctions is None:
            statusFunctions = []
        serial = spi(device=0, port=0)
        self.device = sh1106(serial,rotate=2)
        self.statusFunctions = statusFunctions
        #print logo to device
        self.__initgpio()


    def __initgpio(self):

        #GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        
        for k in ['key1', 'key2', 'key3', 'left', 'up', 'press', 'down', 'right']:
            GPIO.setup(self.key[k], GPIO.IN, pull_up_down=GPIO.PUD_UP)

        #LIPO LOW BATTERY
        #GPIO.setup(lowBat, GPIO.IN,pull_up_down=GPIO.PUD_UP)
        for k in ['key1', 'key2', 'key3', 'press']:
            GPIO.add_event_detect(self.key[k], GPIO.FALLING,bouncetime=300)
        
        for k in ['left', 'down', 'up', 'right']:
            GPIO.add_event_detect(self.key[k], GPIO.BOTH,callback=self.__move, bouncetime=50)
        
    def __move(self, key):
        if GPIO.input(key) == 0:
            self.keypressed[key] = True
            self.keybounce[key] = time.clock()
        else:
            self.keypressed[key] = False

    def isPressed(self, key, bouncetime=0.1):
        if self.keypressed[key] and time.clock()-self.keybounce[key] >= bouncetime:
            self.keybounce[key] = time.clock()
            return True
        else:
            return False
    def dispImage(self, image="coOP_logo.bmp"):
        with canvas(self.device) as draw:
            im = Image.open("coOP_logo.bmp").convert("1")
            draw.bitmap((0,0),im, fill="white")

    def dispText(self, textlist):
        with canvas(self.device) as draw:
            for idx,text in enumerate(textlist):
                draw.text((0,idx*10),text,"white")

    def dispProgress(self, title, progress):
        with canvas(self.device) as draw:
            progpix=progress*64
            draw.text((16,8),title,"white")
            draw.rectangle((32,32,96,42), outline="white", fill="black")
            draw.rectangle((32,32,32+progpix,42), outline="white", fill="white")

    def dispError(self, text):
        with canvas(self.device) as draw:

            #center this plz
            draw.rectangle((8,8,120,56), outline="black", fill="white")
            draw.rectangle((10,10,118,54), outline="white", fill="black")
            for i, line in enumerate(text):
                if len(line)>19:
                    line = line[:19]

                draw.text((64-int(len(line)*2.5), 15 + 15*i),line,"white")
        time.sleep(1)

    def drawListMenu(self, title, menu, pos):
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
        mlistc=["white"] * len(cutout)
        mlistc[relative] = "black"

        #action menu
        #axdist=64
        #alist=["action1", "action2","action3"]
        #alistc=["white"]*len(alist)
        #if apos != 0:
        #   alistc[apos-1]="black"



        with canvas(self.device) as draw:

            #draw title
            draw.rectangle((0,0,128,12), outline="white", fill="white")
            #draw.rectangle((1,10,126,11), outline="black", fill="black")
            draw.text((2,0),title,"black")

            # // STATUS BAR //
            #create better icons
            for i, sf in enumerate(self.statusFunctions):
                if sf() == 1:
                    draw.rectangle((116-10*i,2,124-10*i,10), outline="black", fill="black")
                else:
                    draw.rectangle((116-10*i,2,124-10*i,10), outline="black", fill="white")

            #if is_connected()==1:
            #    draw.rectangle((116,2,124,10), outline="black", fill="black")
            #else:
            #    draw.rectangle((116,2,124,10), outline="black", fill="white")

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


    def dispMenu(self, menu: Menu, mode=0):
        """default mode 0, mode 1 returns val"""

        pos = 0
        menulist = menu.getlist()
        menlen = len(menulist)
        self.drawListMenu(menu.name, menulist, pos)
        while True:

            if self.isPressed(self.key['down']):
                pos = self.listMove(pos, 1, menlen)
                self.drawListMenu( menu.name, menulist, pos)

            elif self.isPressed(self.key['up']):
                pos = self.listMove(pos, -1, menlen)
                self.drawListMenu(menu.name, menulist, pos)

            elif GPIO.event_detected(self.key['key1']):
                if mode == 0:
                    if menu.hasargs:
                        exit = menu.getfunc(pos)(self, menu.getval(pos), menu.getargs(pos))
                    else:
                        exit = menu.getfunc(pos)(self, menu.getval(pos))
                        
                    if exit:
                        break

                elif mode == 1:
                    return menu.getval(pos)
                else:
                    break

                self.drawListMenu(menu.name, menulist, pos)

            elif GPIO.event_detected(self.key['key3']):
                break
            else:
                sleep(0.00001)

    def drawKeyboard(self, word, position):
        with canvas(self.device) as draw:
            draw.text((10, 5), word, "white")
            ioff = 20
            joff = 14
            iofft = 0
            jofft = 3
            for i, row in enumerate(self.keyboard):
                for j, field in enumerate(row):
                    if (i, j) == position:
                        draw.rectangle((joff+j*10, ioff+i*10, joff+j*10+10, ioff+i*10+10), outline="white", fill="white")
                        draw.text((joff+j*10+jofft, ioff+i*10+iofft), field, "black")
                    else:
                        draw.text((joff+j*10+jofft, ioff+i*10+iofft), field, "white")

    def dispKeyboard(self, word = ""):
        """opens a keyboard, returns entered word"""
        
        i = 0
        j = 0
        update = False
        self.drawKeyboard(word, (i, j))

        while True:
            #TODO make this more elegant
            if self.isPressed(self.key['down'], 0.075):
                i = self.listMove(i, 1, 4)
                update = True

            elif self.isPressed(self.key['up'], 0.075):
                i = self.listMove(i, -1, 4)
                update = True

            elif self.isPressed(self.key['left'], 0.075):
                j = self.listMove(j, -1, 10)
                update = True

            elif self.isPressed(self.key['right'], 0.075):
                j = self.listMove(j, 1, 10)
                update = True
                
            elif GPIO.event_detected(self.key['press']):
                if len(word)<19:
                    word = word + self.keyboard[i][j]
                    update = True

            elif GPIO.event_detected(self.key['key1']):
                if word != "":
                    word = word [:-1]
                update = True

            elif GPIO.event_detected(self.key['key2']):
                return ""

            elif GPIO.event_detected(self.key['key3']):
                return word
            
            if update:
                self.drawKeyboard(word, (i, j))
                update = False


    def listMove(self, pos, step, size):
        return (pos+step)%size


