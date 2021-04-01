from threading import Event, Thread
from time import sleep

shutdownTimeout = 1


class ProgramManager:
    def __init__(self, initialProgram):
        # TODO probably should be threadsafe maybe?
        self.programStack = [initialProgram]
        self.currentProgramId = 0
        self.somethingHappened = Event()
        self.whatHappened = ""
        self.killMe = Event()
        self.activeThread = Thread(target=self.mainLoop)
        self.activeThread.start()
        self.programStack[self.currentProgramId].activate(self)

    def mainLoop(self):
        while not self.killMe.isSet():
            somethingActuallyHappened = self.somethingHappened.wait(shutdownTimeout)
            if somethingActuallyHappened:
                print("something happened")
                # execute the next program or exit the current one or sth

                if self.whatHappened == "new":
                    self.programStack[self.currentProgramId].deactivate()
                    self.currentProgramId += 1
                    self.programStack[self.currentProgramId].activate(self)

                elif self.whatHappened == "exit":
                    self.programStack[self.currentProgramId].deactivate()
                    if self.currentProgramId > 0:
                        self.currentProgramId -= 1
                        tmp = self.programStack.pop(-1)
                        del tmp

                    self.programStack[self.currentProgramId].activate(self)

                self.somethingHappened.clear()

    def startNewProgram(self, program):
        while self.somethingHappened.isSet():
            # TODO evtl sleep timer hier
            sleep(0.25)
            pass
        self.programStack.append(program)
        self.whatHappened = "new"
        self.somethingHappened.set()

    def exitProgram(self):
        while self.somethingHappened.isSet():
            # TODO evtl sleep timer hier
            sleep(0.25)
            pass

        self.whatHappened = "exit"
        self.somethingHappened.set()