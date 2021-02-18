import time, os, datetime
import shutil as sh
import usb.core
from os import path

# from subprocess import *
from coop1.core.device import Device, Menu, key

# GLOBALS


VENDOR = 0x2367
PRODUCT = 0x0002
MOUNT_DIR = "/media/op1"
USBID_OP1 = "*Teenage_OP-1*"

op1path = MOUNT_DIR
homedir = "/home/pi"


def initFile():
    mkdir(homedir + "/projects/")
    mkdir(homedir + "/samplepacks/")
    mkdir(MOUNT_DIR)


###shoutouts to tink3rtanker
## do not work tho
def is_connected():
    return usb.core.find(idVendor=VENDOR, idProduct=PRODUCT) is not None


def getmountpath():
    o = os.popen("readlink -f /dev/disk/by-id/" + USBID_OP1).read()
    if USBID_OP1 in o:
        return False
    else:
        return o.rstrip()


def mountdevice():
    source = getmountpath()
    target = MOUNT_DIR
    if target is False:
        return False

    ret = os.system("sudo mount {} {}".format(source, target))
    if ret not in (0, 8192):
        return False
    return True


def unmountdevice():
    target = MOUNT_DIR
    ret = os.system("sudo umount {}".format(target))
    if ret != 0:
        return False
    return True


####


def copy_and_overwrite(from_path, to_path):
    # if os.path.exists(to_path):
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
            if name == "" or not os.path.isdir(path.join(homedir, "projects", name)):
                break

        if name == "":
            return False

        newdir = path.join(homedir, "projects", name)
        # mkdir(newdir)

        mounted = mountdevice()
        if not mounted:
            device.dispError(["Dear OP-1,", "Where Art Thou"])
            return False

        device.dispProgress("saving Tape...", 0)
        sh.copytree(path.join(op1path, "tape"), path.join(newdir, "tape"))

        device.dispProgress("saving Synth...", 0.6)
        sh.copytree(
            path.join(op1path, "synth", "user"), path.join(newdir, "synth", "user")
        )

        device.dispProgress("saving Drums...", 0.8)
        sh.copytree(
            path.join(op1path, "drum", "user"), path.join(newdir, "drum", "user")
        )

        print("copy abgeschlossen")

        unmounted = unmountdevice()
        if not unmounted:
            device.dispError(["unmount failed", "RIP in Pepperoni"])
            return False

        device.dispProgress("successfully saved", 1)
        time.sleep(0.5)
        return True
    else:
        device.dispError(["404", "OP-1 not found"])
        return False


def overwrite(device, project):
    # prompt full save/ARE YOU SURE ABOUT THAT?
    prompt = Menu("Are you sure about that?", [("yes", nothing), ("no", nothing)])
    sure = device.dispMenu(prompt, 1)

    if sure == "no":
        return False

    if is_connected():

        savdir = path.join(homedir, "projects", project)
        # mkdir(newdir)

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
        tapeDir = path.join(op1path, "tape")
        for i, tape in enumerate(os.listdir(tapeDir)):
            copy_and_overwrite(
                path.join(tapeDir, tape), path.join(savdir, "tape", tape)
            )
            device.dispProgress("saving Tape...", 0.2 * i)

        device.dispProgress("saving Synth...", 0.8)
        synthDir = path.join(op1path, "synth", "user")
        for i, synth in enumerate(os.listdir(synthDir)):
            copy_and_overwrite(
                path.join(synthDir, synth), path.join(savdir, "synth", "user", synth)
            )

        device.dispProgress("saving Drums...", 0.9)
        drumDir = path.join(op1path, "drum", "user")
        for i, drum in enumerate(os.listdir(drumDir)):
            copy_and_overwrite(
                path.join(drumDir, drum), path.join(savdir, "drum", "user", drum)
            )

        print("copy abgeschlossen")

        unmounted = unmountdevice()
        if not unmounted:
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

        loaddir = path.join(homedir, "projects", project)
        # mkdir(newdir)

        mounted = mountdevice()
        if not mounted:
            device.dispError(["Dear OP-1,", "Where Art Thou"])
            return False

        device.dispProgress("loading Tape...", 0)

        for i, tape in enumerate(os.listdir(path.join(loaddir, "tape"))):
            copy_and_overwrite(
                path.join(loaddir, "tape", tape), path.join(op1path, "tape", tape)
            )
            device.dispProgress("loading Tape...", 0.2 * i)

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

        projects.append(filename)

    projects.sort()

    save = Menu(
        "Save Project", [("NEW PROJECT", saveNew)] + [(p, overwrite) for p in projects]
    )
    device.dispMenu(save)


def loadCaller(device, val):

    directory = homedir + "/projects/"
    projects = []

    for filename in os.listdir(directory):

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

        samplepacks.append(filename)

    samplepacks.sort()
    if len(samplepacks) == 0:
        samplepacks.append("no samplepacks found")
        actions = [nothing]
    else:
        actions = [load] * len(samplepacks)

    samples = Menu("Samplepacks", zip(samplepacks, actions))
    device.dispMenu(samples)


def restart(device, val):
    os.system("sudo reboot")


def opc(device, val):

    main = Menu(
        "OP-1 Companion", [("save project", saveCaller), ("load project", loadCaller)]
    )
    device.dispMenu(main)
