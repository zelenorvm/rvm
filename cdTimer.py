try:
    # for Python2
    from Tkinter import *
    import Tkinter as tk
except ImportError:
    # for Python3
    from tkinter import *
    import tkinter as tk

import settings
import sys

class screenTimer:
    def __init__(self, master,timeVal):
        self.master = master 
        self.state = False
        self.minutes = 0
        self.seconds = timeVal

        self.mins = 0
        self.secs = 0

        self.display = tk.Label(master,font=('Times',35, 'bold'),bg="white", textvariable="")
        self.display.config(text="00:00")
        self.display.place(x=0,y=0)
        self.state = True
        self.mins = self.minutes
        self.secs = self.seconds
        self.countdown()

    def countdown(self):
        """Displays a clock starting at min:sec to 00:00, ex: 25:00 -> 00:00"""

        if self.state == True and settings.timerStatus == 1:
            if self.secs < 10:
                if self.mins < 10:
                    self.display.config(text="0%d : 0%d" % (self.mins, self.secs))
                else:
                    self.display.config(text="%d : 0%d" % (self.mins, self.secs))
            else:
                if self.mins < 10:
                    self.display.config(text="0%d : %d" % (self.mins, self.secs))
                else:
                    self.display.config(text="%d : %d" % (self.mins, self.secs))

            if (self.mins == 0) and (self.secs == 0):
                #self.display.config(text="Done!")
                self.display.config(text="00:00")
                self.state = False
                settings.performCycle = False
                print '\n Timer is now 0'
                #settings.LidStat = False
            else:
                if self.secs == 0:
                    self.mins -= 1
                    self.secs = 59
                else:
                    self.secs -= 1

                self.master.after(1000, self.countdown)
        
        elif self.state == True and settings.timerStatus == 0:
            self.mins = self.minutes
            self.secs = 20
            #settings.performCycle = True
            self.display.config(text="%d : %d" % (self.mins, self.secs))
            self.master.after(1000, self.countdown)

        else:
            self.master.after(100, self.countdown)
        

    def start(self):
        if self.state == False:
            self.state = True
            self.mins = self.minutes
            self.secs = self.seconds

"""
root = tk.Tk()
my_timer = screenTimer(root,30)
    
root.mainloop()

"""
