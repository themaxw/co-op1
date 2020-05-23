import time,os,datetime
import shutil as sh
import usb.core
#from subprocess import *
from device import Device, Menu, key

#GLOBALS



VENDOR = 0x2367
PRODUCT = 0x0002
MOUNT_DIR = "/media/op1"
USBID_OP1 = "*Teenage_OP-1*"

op1path=MOUNT_DIR
homedir="/home/pi/opc"


def initFile():
    mkdir(homedir + "/projects/")
    mkdir(homedir + "/samplepacks/")
    mkdir(MOUNT_DIR)

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

        
def copy_and_overwrite(from_path, to_path):
    #if os.path.exists(to_path):
    #    os.system("sudo rm "+ to_path)
    os.system("sudo cp " + from_path + " " + to_path)


def mkdir(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def saveNew(device, val):
    """saves project as new project
    
    Arguments:
        device {Device} -- Device being used
        val {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    if is_connected():
        while True:
            name = ""
            name = device.dispKeyboard(name)
            if name == "" or not os.path.isdir(homedir + "/projects/" + name):
                break

        if name == "":
            return False

        newdir = homedir+ "/projects/"+name+"/"
        #mkdir(newdir)

        mounted = mountdevice()
        if not mounted:
            device.dispError(["Dear OP-1,", "Where Art Thou"])
            return False

        device.dispProgress("saving Tape...", 0)
        sh.copytree("/media/op1/tape", newdir+"tape")

        device.dispProgress("saving Synth...", 0.6)
        sh.copytree("/media/op1/synth/user", newdir+"synth/user")

        device.dispProgress("saving Drums...", 0.8)
        sh.copytree("/media/op1/drum/user", newdir+"drum/user")


        print("copy abgeschlossen")

        unmounted = unmountdevice()
        if not unmounted:
            device.dispError( ["unmount failed", "RIP in Pepperoni"])
            return False

        device.dispProgress( "successfully saved", 1)
        time.sleep(0.5)
        return True
    else:
        device.dispError( ["404", "OP-1 not found"])
        return False



def overwrite(device, project):
    #prompt full save/ARE YOU SURE ABOUT THAT?
    prompt = Menu("Are you sure about that?", [("yes", nothing), ("no", nothing)])
    sure = device.dispMenu(prompt, 1)
    
    if sure == "no":
        return False

    if is_connected():

        savdir = homedir+ "/projects/"+project+"/"
        #mkdir(newdir)

        mounted = mountdevice()
        if not mounted:
            device.dispError(["Dear OP-1,", "Where Art Thou"])
            return False

        # device.dispProgress("saving Tape...", 0)
        # copy_and_overwrite("/media/op1/tape", savdir+"tape")

        # device.dispProgress("saving Synth...", 0.6)
        # copy_and_overwrite("/media/op1/synth/user", savdir+"synth/user")

        # device.dispProgress("saving Drums...", 0.8)
        # copy_and_overwrite("/media/op1/drum/user", savdir+"drum/user")
        device.dispProgress("saving Tape...", 0)
        for i, tape in enumerate(os.listdir( "/media/op1/tape/")):
            copy_and_overwrite( "/media/op1/tape/"+tape, savdir+"tape/"+tape)
            device.dispProgress("saving Tape...", 0.2*i)

        device.dispProgress("saving Synth...", 0.8)
        for i, synth in enumerate(os.listdir("/media/op1/synth/user/")):
            copy_and_overwrite("/media/op1/synth/user/"+synth, savdir+"synth/user/"+synth)

        device.dispProgress("saving Drums...", 0.9)
        for i, drum in enumerate(os.listdir("/media/op1/drum/user/")):
            copy_and_overwrite("/media/op1/drum/user/"+drum, savdir+"drum/user/"+drum)


        print("copy abgeschlossen")

        unmounted = unmountdevice()
        if not unmounted :
            device.dispError(["unmount failed", "RIP in Pepperoni"])
            return False

        device.dispProgress("successfully saved", 1)
        time.sleep(0.5)
        return True
    else:
        device.dispError(["404", "OP-1 not found"])
        return False

def load(device, project):
    prompt = Menu("Are you sure about that?", [("yes", nothing), ("no", nothing)])
    sure = device.dispMenu(prompt, 1)
    if sure == "no":
        return False

    if is_connected():

        loaddir = homedir+ "/projects/"+project+"/"
        #mkdir(newdir)

        mounted = mountdevice()
        if not mounted:
            device.dispError(["Dear OP-1,", "Where Art Thou"])
            return False

        device.dispProgress("loading Tape...", 0)
        for i, tape in enumerate(os.listdir(loaddir+"tape/")):
            copy_and_overwrite(loaddir+"tape/"+tape, "/media/op1/tape/"+tape)
            device.dispProgress("loading Tape...", 0.2*i)

        # device.dispProgress("loading Synth...", 0.8)
        # for i, synth in enumerate(os.listdir(loaddir+"synth/user/")):
        #     copy_and_overwrite(loaddir+"synth/user/"+synth, "/media/op1/synth/user/"+synth)

        # device.dispProgress("loading Drums...", 0.9)
        # for i, drum in enumerate(os.listdir(loaddir+"drum/user/")):
        #     copy_and_overwrite(loaddir+"drum/user/"+drum, "/media/op1/drum/user/"+drum)


        print("load abgeschlossen")

        unmounted = unmountdevice()
        if not unmounted:
            device.dispError(["unmount failed", "RIP in Pepperoni"])
            return False

        device.dispProgress("successfully loaded", 1)
        time.sleep(0.5)
        return True
    else:
        device.dispError(["404", " OP-1 not found"])
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

    save = Menu("Save Project", [("NEW PROJECT", saveNew)] + [(p, overwrite) for p in projects])
    device.dispMenu(save)

def loadCaller(device, val):

    directory = homedir + "/projects/"
    projects = []

    for filename in os.listdir(directory):

        fullPath = directory + filename
        projects.append(filename)

    projects.sort()

    if len(projects) == 0:
        projects.append("no projects found", nothing)
    else:
        projects = [(p, load) for p in projects]

    print(projects)
    loadM = Menu("Load Project", projects)
    device.dispMenu(loadM)

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
        
    samples = Menu("Samplepacks", zip(samplepacks, actions))
    device.dispMenu(samples)


    
def restart(device, val):
    os.system("sudo reboot")

def opc(device, val):
    
    main = Menu("OP-1 Companion", [("save project", saveCaller), ("load project", loadCaller)])
    device.dispMenu(main)
