from device import Device, Menu
from filetree import File
class FileBrowser:
    def __init__(self, device, path):
        self.f = File(path)
        self.device = device

    def changeDir(self, device, val):
        if val == "..":
            self.f = self.f.parent()
        else:
            for d in self.f.dirs:
                if d.basename == val:
                    self.f = d
                    break
        self.makeFileBrowser()

    def nothing(self, device, val):
        pass

    def makeFileBrowser(self):
        directoryList = [("..", self.changeDir)]
        directoryList.extend([(x.basename, self.changeDir) for x in self.f.dirs if not x.basename.startswith(".")])
        directoryList.extend([(x.basename, self.nothing) for x in self.f.files])
        fileMenu = Menu(self.f.path, directoryList)
        self.device.dispMenu(fileMenu)

def fileBrowser(device, val):
    fb = FileBrowser(device, "/home/pi/")
    fb.makeFileBrowser()