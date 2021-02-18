from PIL import Image, ImageDraw

class Listmenu(object):
    def __init__(self, name, items, device, active=True, position=0):
        self.name = name
        self.items = items
        self.length = len(items)
        self.position = position
        self.device = device

        self._menuItemOffset = 9
        self._xOffset = 5
        self._yOffset = 4
        self._animationFrames = 3
        
        self.setupTextImage()
        if active:
            self.updateDisplay()


    def setupTextImage(self):
        self.textImage = Image.new(self.device.device.mode, (self.device.device.size[0], self._menuItemOffset*self.length))
        draw = ImageDraw.Draw(self.textImage) 
        for i, item in enumerate(self.items):
            draw.text((self._xOffset, i*self._menuItemOffset), item, "white")

                
    def getOffset(self):
        if self.length>5:
            if self.position == 0 or self.position == 1:
                offset = 0
                relative = self.position
            elif self.position == self.length-1 or self.position == self.length-2:
                offset = self.length-5
                relative = 4-(self.length-1-self.position)
            else:
                offset = self.position-2
                relative = 2
        else:
            offset = self.items
            relative = self.position

        return offset, relative

    def updateDisplay(self, movement=None):
        frame, draw = self.device.baseFrame(fullscreen=False)
        offset, relative = self.getOffset()
        if movement is None:
            textCropped = self.textImage.crop((0, offset*self._menuItemOffset, 128, (offset+5)*self._menuItemOffset))           
            frame.paste(textCropped, (0, self._yOffset))    
            draw.rectangle((self._xOffset, relative*self._menuItemOffset+self._yOffset, 128 - self._xOffset, ((relative+1)*10)+self._yOffset), outline="white", fill=None)
            self.device.addFrames([frame], fullscreen=False)
        else:

            for i in range(self._animationFrames):
                pass


if __name__ == "__main__":
    from screen import Device
    from statusFunctions import is_connected, wifi_status
    scr = Device([is_connected, wifi_status], 10)
    menu = Listmenu("test", ["1", "3", "2", "langes Item jaja", "ich bin auch da", "reee"], scr)
    from time import sleep
    sleep(10)
    scr.stop()