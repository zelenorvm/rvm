
#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
#########################################################################################################################################
#																	#
#		File Name  :	mainPrgm.py												#
#		File Author :	Anil Kumar Dhyani	                                                                                #
#               Description : RVM program for Rajasthan                                                                                 #					    
#																	#
#########################################################################################################################################
'''
try:
    # for Python2
    from Tkinter import *   
    import Tkinter as tk
except ImportError:
    # for Python3
    from tkinter import *
    import tkinter as tk

from functools import partial
from PIL import ImageTk, Image
import os
import sys
import string
import PIL
import subprocess
from subprocess import Popen, PIPE
import tkMessageBox
import time
import requests
import json
import threading

from threading import Thread,Timer
sys.path.insert(0, '/home/pi/Downloads/zel_Raj/')
#sys.path.insert(0, '/home/anil/zel_Raj/')
from os import walk
from escposprinter import *
#from escposprinter.escpos import EscposIO, Escpos
import random
from random import randint
import cdTimer 
import settings
import pigpio
from itertools import count
from dbOper import execQuery

encoding = "utf-8" 
on_error = "replace"


initscreenPath="/home/pi/Downloads/zel_Raj/gui/staticImages/"
staticImgPath="/home/pi/Downloads/zel_Raj/gui/Software_Kiosk/Gifimages/Insert/"
imagesEnglish="/home/pi/Downloads/zel_Raj/gui/Software_Kiosk/English/"
imagesHindi="/home/pi/Downloads/zel_Raj/gui/Software_Kiosk/Hindi/"
imgCoupon="/home/pi/Downloads/zel_Raj/gui/couponImages/"
imgGui="/home/pi/Downloads/zel_Raj/gui/guiImages/"
imgBackground="/home/pi/Downloads/zel_Raj/gui/Software_Kiosk/Background/"
imgGif="/home/pi/Downloads/zel_Raj/gui/Software_Kiosk/Gifimages/"
imgButtons="/home/pi/Downloads/zel_Raj/gui/Software_Kiosk/Keypad/"

VID_PATH="/home/pi/Downloads/zel_Raj/gui/videos/"

#### RPI GPIO PINS

GPIO_LID=5
GPIO_PHOTO_SENS_1=16
GPIO_PHOTO_SENS_2=21
GPIO_RELAY_1=13
GPIO_RELAY_2=19
GPIO_RELAY_3=26

keypadList=["1","2","3","4","5","6","7","8","9","Clr","0","Bksp"]

recycleStatus=False
scrollTicker=None
lblTimer=None
mobileNum=0
optionSelect=0
msgBody=""
SERVERIP="54.187.173.228"
PORT=8001
mainScreen=None
mainScreen1=None
LidStat=False
endRecycleCount=False
driveConveyer=False
crusherCount=0
timeCount = 0
labelImg=None
initScroller=None
backPointer=None
initscreenList=[]
gpioHandle = None
mobEntry=None
oprcycleCount=20
reduceCount = 0
couponSent=False
couponDetails = [
        {"Name" : "Dominos", "Id" : "cp1",  "LabelText": "10% off", "Message" : "Use Coupon Code DISC10 to get 10% off on Dominos Pizza", "Image" : "" } ,
        {"Name" : "Mobikwik", "Id" : "cp2",  "LabelText": "5% CashBack", "Message" : "Use Coupon Code KWIK5 to get 5% CashBack on Prepaid Mobile Recharge", "Image" : "" },
        {"Name" : "Myntra", "Id" : "cp3",  "LabelText": "10% off", "Message" : "Use Coupon Code FEST10 to get 10% off on Myntra", "Image" : "" },
        {"Name" : "PayTm", "Id" : "cp4",  "LabelText": "5% Cashback", "Message" : "Use Coupon Code HOTEL5 to get 5% off on Hotel Booking via Paytm ", "Image" : "" }
        ]

#couponDetails.sort()

class ImageLabel(tk.Label):
    """a label that displays images, and plays them if they are gifs"""
    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
        self.loc = 0
        self.frames = []

        try:
            for i in count(1):
                self.frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass

        try:
            self.delay = im.info['duration']
        except:
            self.delay = 100

        if len(self.frames) == 1:
            self.config(image=self.frames[0])
        else:
            self.next_frame()

    def unload(self):
        self.config(image=None)
        self.frames = None

    def next_frame(self):
        if self.frames:
            self.loc += 1
            self.loc %= len(self.frames)
            self.config(image=self.frames[self.loc])
            self.after(self.delay, self.next_frame)

def changeImg(labelImg,mainScreen):
    global initScroller,initscreenList
    for k in range(0,len(initscreenList)):
        Photo2 = Image.open(initscreenPath + initscreenList[k])
        newPhoto = ImageTk.PhotoImage(Photo2)
        labelImg.configure(image = newPhoto)
        labelImg.image = newPhoto
        time.sleep(0.75)
        mainScreen.update()
    if initScroller is not None:
        print '\n Cancelling Old Init Screen Timer'
        mainScreen.after_cancel(initScroller)
    initScroller  = mainScreen.after(500,lambda :changeImg(labelImg,mainScreen))

def bottleThr(lblbotVal,endcycleButton,master3):
    global crusherCount,gpioHandle,driveConveyer,oprcycleCount,reduceCount
    print '\n Started Bottle Thread'
    #if settings.performCycle is True:
    if oprcycleCount > 1:
        if gpioHandle.read(20) == 1:
            if driveConveyer is True:
                driveConveyer = False
                settings.botCount += 1
            lblbotVal.config(text=str(settings.botCount))
            endcycleButton.config(state="normal")
            #master3.update()
        reduceCount += 1
        if reduceCount == 2:
            oprcycleCount -= 1
            reduceCount = 0
        master3.after(500,lambda :bottleThr(lblbotVal,endcycleButton,master3))
        print '\n Exiting Bottle Thread'
    else:
        stopRoutine(master3,optionSelect)



def checkGpio(lblTimer,master3):
    global driveConveyer,gpioHandle,crusherCount,oprcycleCount
    #gpioHandle.set_mode(16, pigpio.INPUT)
    crusherCount=0
    print '\n Came here in checkGpio'
   
    gpioHandle.write(13,0)
   #while settings.performCycle is True:
    while oprcycleCount > 1:
        if gpioHandle.read(16) == 1:
            print '\n Starting Conveyer'
            driveConveyer = True
            oprcycleCount = 20
            crusherCount=0
            settings.timerStatus=0
            master3.update()
            time.sleep(1)
            settings.timerStatus=1
            settings.performCycle=True
            gpioHandle.write(26,0)
        else:
            if crusherCount == 50:
                gpioHandle.write(13,1)
                gpioHandle.write(26,1)
                crusherCount = 0
            else:
                crusherCount += 1
                master3.update()
                time.sleep(0.25)
    
    print '\n Exiting checkGpio thread'
    return

def sendUsermsg(mobileNum,msgBody):
    API_KEY="1ed86c30-ed32-420d-b5c5-27f28bfadcaa"
    retVal = 0
    msgCommand = 'sudo wget "http://sms.hspsms.com/sendSMS?username=rishabhsfc&message='
    msgCommand += msgBody
    msgCommand += "&sendername=ZELENO"
    msgCommand +="&smstype=TRANS&numbers="
    msgCommand += str(mobileNum)
    msgCommand += "&apikey="
    msgCommand += API_KEY
    msgCommand += '"'
    print '\n msgCommand : ', msgCommand
    try:
        sCommand = subprocess.Popen(msgCommand,shell=True,stdout=subprocess.PIPE)
        sCommand.wait()
        os.system("rm -f sendSMS*")
    except:
            retVal = 1
    return retVal



####################################################################################################################
#                                                                                                                  #
#                                   Send Data to Server                                                            #
#                                                                                                                  #
####################################################################################################################

def webQuery(url,inData):
    headers = {'Content-Type':'application/json'}
    #print '\n url is :', url
    sendReq = requests.post(str(url), data = json.dumps(inData), headers=headers,timeout=5)
    return sendReq.text


def checkServer(SERVERIP,PORT,urlIn,infoVal):
   print '\n infoVal is now :', infoVal
   retVal = json.loads(webQuery("http://" + str(SERVERIP).rstrip() + ":" + str(PORT).rstrip() + urlIn, infoVal))
   return retVal


################################################################################################################################
#															       #
#	                         Return the Files present in a directory                               			       #
#															       #
################################################################################################################################

def getfileList(DIR):
    fList = []
    for (dirpath, dirnames, filenames) in walk(DIR):
        fList.extend(filenames)
    return fList

def operGpios(GPIO_PIN):
    global gpioHandle,LidStat
    ### Pin used for Micro switch for Lid Down
    gpioHandle.set_mode(22, pigpio.INPUT)
    gpioHandle.set_mode(25, pigpio.INPUT)
    gpioHandle.write(int(GPIO_PIN),0)
    tryCatch = 0
    prevTime = time.time()
    currentTime = 0.0
    diffTime = 0.0
    if int(GPIO_PIN) == 5 :
        while True:
            currentTime = time.time()
            diffTime = currentTime - prevTime
            #print '\n diffTime is :', diffTime
            if diffTime > 2.4 :
                break
            if gpioHandle.read(22) == 1 :
                if tryCatch == 10 :
                    break
                else:
                    tryCatch += 1
    elif int(GPIO_PIN) == 6:
        while True:
            currentTime = time.time()
            diffTime = currentTime - prevTime
            #print '\n diffTime is :', diffTime
            if diffTime > 2.4 :
                break
            if gpioHandle.read(25) == 1 :
                if tryCatch == 10:
                    break
                else:
                    tryCatch += 1
    gpioHandle.write(int(GPIO_PIN),1)
    if int(GPIO_PIN) == 5:
        with open("/home/pi/Lidstat.txt", "w") as text_file:
            text_file.write("Open")
    else:
        with open("/home/pi/Lidstat.txt", "w") as text_file:
            text_file.write("Close")
    
    if LidStat is True:
        LidStat = False
    else:
        LidStat = True

'''
#################################################
#						#
#	Create a Timer Object			#
#						#
#################################################

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

'''

class MyGifLabel(Label):
    def __init__(self, master, filename):
        im = Image.open(filename)
        seq =  []
        try:
            while 1:
                seq.append(im.copy())
                im.seek(len(seq)) # skip to next frame
        except EOFError:
            pass # we're done

        try:
            self.delay = im.info['duration']
        except KeyError:
            #self.delay = 100
            self.delay = 100

        first = seq[0].convert('RGBA')
        self.frames = [ImageTk.PhotoImage(first)]

        Label.__init__(self, master, image=self.frames[0])

        temp = seq[0]
        for image in seq[1:]:
            temp.paste(image)
            frame = temp.convert('RGBA')
            self.frames.append(ImageTk.PhotoImage(frame))

        self.idx = 0

        self.cancel = self.after(self.delay, self.play)

    def play(self):
        self.config(image=self.frames[self.idx])
        self.idx += 1
        if self.idx == len(self.frames):
            self.idx = 0
        self.cancel = self.after(self.delay, self.play)        



def scrollingImg(Screen1,lblimgScroller):
    global scrollTicker,staticimgList,staticImgPath
    for i in range(0,len(staticimgList)):
        Photo1 = Image.open(staticImgPath + staticimgList[i])
        newPhoto = ImageTk.PhotoImage(Photo1)
        lblimgScroller.configure(image = newPhoto)
        lblimgScroller.image = newPhoto
        time.sleep(0.15)
        Screen1.update_idletasks()

    scrollTicker = Screen1.after(1500,lambda :scrollingImg(Screen1,lblimgScroller))

def endScreen(currentScreen,prevScreen):
    global labelImg
    currentScreen.destroy()
    prevScreen.deiconify()
    initVariables()
    changeImg(labelImg,prevScreen) 


def backPrgm(t1,t2):
    global lblTimer,mainScreen,scrollTicker,labelImg,mainScreen,recycleStatus
    print '\n Going back to Prev Screen'
    if recycleStatus is False :
        print '\n I came here'
        initVariables()
        t1.destroy()
        t2.deiconify()
        changeImg(labelImg,t2) 
    else:
        print '\n I am here'
        t1.withdraw()
        if t2 is not None:
            t2.deiconify()
            #changeImg(labelImg,t2) 
    return


def backRoutine(currentScreen,previousScreen):
    global recycleStatus,timeCount,labelImg
    if recycleStatus is False:
        timeCount = 0
        currentScreen.withdraw()
        previousScreen.deiconify()
        changeImg(labelImg,previousScreen) 
    return


def randN(n):
    newVal = 0
    assert n <= 10 
    l = list(range(10)) # compat py2 & py3
    while l[0] == 0:
        random.shuffle(l)
    return int(''.join(str(d) for d in l[:n]))

def initVariables():
    global mobileNum,recycleStatus,msgBody,scrollTicker,lblTimer,endRecycleCount,timeCount,backPointer,gpioHandle,reduceCount,couponSent
    recycleStatus=False
    endRecycleCount=False
    scrollTicker=None
    lblTimer=None
    backPointer=None
    couponSent=False

    mobileNum=0
    optionSelect=0
    timeCount=0
    settings.botCount=0 
    settings.timerStatus=0
    msgBody=""
    reduceCount = 0 
    #settings.playVideo = True
    settings.performCycle=False
    if gpioHandle is None:
        gpioHandle = pigpio.pi()
    else:
        print '\n Clearing the GPIO Status'
        gpioHandle.stop()
        gpioHandle = pigpio.pi()

def randN(n):
    newVal = 0
    assert n <= 10 
    l = list(range(10)) # compat py2 & py3
    while l[0] == 0:
        random.shuffle(l)
    return int(''.join(str(d) for d in l[:n]))


def prReceipt(mobNum,couponName,botCount):
    Epson = printer.Usb(0x0519,0x2013,0x04,0x81,0x03)
    #Epson = printer.Usb(0x0456,0x0808,0x04,0x81,0x03)
    Epson.text('Coupon Slip\n\n')
    Epson.text("Machine Id :" + settings.MACHINE_ID + "\n")
    Epson.text("Ticket No :" + str(randN(10))  + "\n")
    Epson.text("Mobile Number : " + str(mobNum) + "\n")
    Epson.text("Bottles Recycled :" + str(botCount) + "\n") 
    Epson.text("Coupon Name :" + couponName + "\n")
    Epson.text("Time :" + str(time.strftime("%d/%m/%Y" "%H:%M:%S")) + "\n")
    Epson.cut(mode="FULL")
    return

def printReceipt(master6,mobNum,couponText,Option):
    global mainScreen
    """
    printCommand = "sudo python /home/pi/Downloads/zel_Raj/gui/printer.py " + str(mobNum) + " '" + str(couponText)  + "' "  + str(settings.botCount)
    print '\n printCommand is :', printCommand
    if Option is "Yes" and len(couponText) > 4:
        try:
            pCommand = subprocess.Popen(printCommand ,shell=True,stdout=subprocess.PIPE)
            pCommand.wait()
        except :
            print '\n Cannot print Coupon'
    """
    try:
        prReceipt(str(mobNum), str(couponText) , str(settings.botCount))
    except:
        print '\n Got Error'

    endScreen(master6,mainScreen)


def receiptWindow(master5,mobileNum,msgBody):
    #### Get All Available Coupon For the Specified Value 
    global mainScreen,backPointer
    """
    if backPointer is not None:
        print '\n cancelling Backpointer'
        master5.after_cancel(backPointer)
    """
    print '\n Destroying master5 window'
    master5.destroy()
    time.sleep(0.1)
    master6 = tk.Toplevel()
    ws6 = master6.winfo_screenwidth() # width of the screen
    hs6 = master6.winfo_screenheight() # height of the screen
     
    if optionSelect == 1:
        bgPhoto = Image.open(imagesEnglish + "Screen10/" + "Background.jpg")
        imgBack = Image.open(imagesEnglish + "Screen10/" +  "Back.jpg")
        imgYes = Image.open(imagesEnglish + "Screen10/" +  "Yes.jpg")
        imgNo = Image.open(imagesEnglish + "Screen10/" +  "No.jpg")

    else:
        bgPhoto = Image.open(imagesHindi + "Screen8/" + "Background.jpg")
        imgBack = Image.open(imagesHindi + "Screen8/" +  "Back.jpg")
        imgYes = Image.open(imagesHindi + "Screen8/" +  "Yes.jpg")
        imgNo = Image.open(imagesHindi + "Screen8/" +  "No.jpg")

    bgPhoto = bgPhoto.resize((ws6,hs6), PIL.Image.ANTIALIAS)
    bgPhoto = ImageTk.PhotoImage(bgPhoto)
    lbl6Background = Label(master6,width=ws6,height=hs6, image=bgPhoto)
    lbl6Background.photo = bgPhoto
    lbl6Background.pack(fill=BOTH, expand = YES)

    master6.config(width =ws6, height=hs6)

    """ 
    imgBack = imgBack.resize((300,150), PIL.Image.ANTIALIAS)
    imgBack = ImageTk.PhotoImage(imgBack)
    backButton = tk.Button(lbl6Background,highlightthickness=0,bd=0,bg="white",image=imgBack,command=lambda: backRoutine(master6,oldWindow))
    backButton.image = imgBack 
    backButton.place(x=100,y=50)
    """ 

    imgYes = imgYes.resize((450,150), PIL.Image.ANTIALIAS)
    imgYes = ImageTk.PhotoImage(imgYes)
    yesButton = tk.Button(lbl6Background,highlightthickness=0,bd=0,image=imgYes,command=lambda: printReceipt(master6,mobileNum,msgBody,"Yes"))
    yesButton.image = imgYes
    yesButton.place(x=240,y=hs6/2 - 20)
     
    imgNo = imgNo.resize((450,150), PIL.Image.ANTIALIAS)
    imgNo = ImageTk.PhotoImage(imgNo)
    noButton = tk.Button(lbl6Background,highlightthickness=0,bd=0,image=imgNo,command=lambda: endScreen(master6,mainScreen))
    noButton.image = imgNo
    noButton.place(x=700,y=hs6/2 - 20)
     
    master6.attributes("-fullscreen", True)
    master6.mainloop()



def restartRecycling(master5):
    global mobileNum
    retSts = 1
    try:
        retSts = sendUsermsg(mobileNum, msgBody)
        if retSts == 0:
            print '\n Coupon Send to user'
        else:
            print '\n Could Not Send Coupon to user'
    except:
        print '\n Cannot Execute '
    receiptWindow(master5,mobileNum,msgBody)
     

def sendCoupon(btnVal,mobileNum,master5):
    global msgBody,couponSent
    couponFound = 0
    print '\n btnVal is :', btnVal
    for i in range(0,len(couponDetails)):
        if couponDetails[i]["Id"] == btnVal:
            print '\n You have Selected :', couponDetails[i]["Name"]
            couponFound = 1
            #btnVal.configure(bg="red")
            msgBody = couponDetails[i]["Message"]
            master5.update()
            break
    insQuery = "Insert into Transaction(mobileNum,bottleCount,selCoupon) VALUES ('"
    if couponFound == 0:
        print '\n Coupon Not found '
    else:
        if couponSent is False:
            print '\n Coupon Found Inserting Record in Database'
            insQuery += str(mobileNum)
            insQuery += "',"
            insQuery += str(settings.botCount)
            insQuery += ",'"
            insQuery += str(couponDetails[i]["Name"])
            insQuery += "')"
            print '\n Insert Query is :', insQuery
            try:
                execQuery(insQuery)
                print '\n Inserted Record Successfully'
            except:
                print '\n Cannot insert in database'
            couponSent = True

def moveBack(master5):
    global backPointer,labelImg,mainScreen
    if backPointer is not None:
        print '\n Cancelling Coupon screen Pointer'
        master5.after_cancel(backPointer)
    master5.destroy()
    if mainScreen is not None:
        mainScreen.deiconify()
        changeImg(labelImg,mainScreen) 


def getCouponlist(oldWindow,mobileNum,bottleCount):
    #### Get All Available Coupon For the Specified Value 
    global optionSelect
    backPointer = None
    couponVal = {}
    oldWindow.destroy()
    master5 = tk.Toplevel()
    ws5 = master5.winfo_screenwidth() # width of the screen
    hs5 = master5.winfo_screenheight() # height of the screen

    if optionSelect == 1:
        coverPhoto = Image.open(imagesEnglish + "Screen10/" + "Background.jpg")
        imgConfirm = Image.open(imagesEnglish + "Screen10/" +  "confirm.jpg")

    else:
        coverPhoto = Image.open(imagesHindi + "Screen10/" + "Background.jpg")
        imgConfirm = Image.open(imagesHindi + "Screen10/" +  "confirm.jpg")

    coverPhoto = coverPhoto.resize((ws5,hs5), PIL.Image.ANTIALIAS)
    coverPhoto = ImageTk.PhotoImage(coverPhoto)
    lbl5Background = Label(master5,width=ws5,height=hs5, image=coverPhoto)
    lbl5Background.photo = coverPhoto
    lbl5Background.pack(fill=BOTH, expand = YES)

    master5.config(width =ws5, height=hs5)

    couponList = []
    for (dirpath, dirnames, filenames) in walk(imgCoupon):
        couponList.extend(filenames)

    if len(couponList) == 0:
        tkMessageBox("Info", "No Coupons Available at the moment.. Please try after Sometime")
        return

    lblCoupon = Label(lbl5Background,width=250,height=2,font=('Times',18, 'bold'),fg="Black",bg="white",text="Select Coupon")
    lblCoupon.place(x=50,y= 50)
    
    couponButtons = [
                    ['cp1','cp2','cp3', 'cp4'],
                    ['cp5','cp6','cp7', 'cp8'],
                 
                    ]
    r = 0
    c = 0
    xPad = 0
    yPad = 0
    lblXpad = 0
    lblYpad = 0

    for i in range(0,len(couponList)):
        rImg = Image.open(imgCoupon + couponList[i])
        newImg = ImageTk.PhotoImage(rImg)
        cycleButton = tk.Button(lbl5Background,highlightthickness=0,bd=0,image=newImg)
        cycleButton.config(width=100, height=100,command = partial(sendCoupon, couponButtons[r][c],mobileNum,master5))
        cycleButton.image = newImg
        cycleButton.place(x= 50 + xPad ,y = 200 + yPad)
        lblInfo = Label(lbl5Background, text=couponDetails[i]["LabelText"],font=('Times',15, 'bold'),height=1,bg="white",fg="#040459",highlightthickness=0,bd=0)
        lblInfo.place(x= 25 + lblXpad ,y = 350 + lblYpad)
  
        if i == 4 or i == 8:
            r += 1
            yPad += 200
            lblYpad += 200
            xPad = 0
        else:
            xPad += 200
            lblXpad += 200
            c += 1

    imgConfirm = ImageTk.PhotoImage(imgConfirm)
    confirmButton = tk.Button(lbl5Background,highlightthickness=0,bd=0,image=imgConfirm,command=lambda: restartRecycling(master5))
    confirmButton.image = imgConfirm
    confirmButton.place(x=775,y=550)
    
    master5.attributes("-fullscreen", True)
    master5.mainloop()



#############################################################################################
#                                                                                           #
#                                                                                           #
#                      Get The Mobile Number from the User                                  #
#                                                                                           #
#                                                                                           #
#############################################################################################


def buttonClicked(buttonVal,mobTxtBox):
    Val = '' 
    newVal = ''
    Val = mobTxtBox.get('1.0',END).rstrip()
    if buttonVal == "Clr":
        mobTxtBox.delete('1.0',END)

    elif buttonVal == "Bk":
        newVal = Val[:-1]
        mobTxtBox.delete('1.0',END)
        mobTxtBox.insert('1.0',str(newVal))
   
    elif len(Val) > 9 :
        return
    else:
        mobTxtBox.insert(END,str(buttonVal))

def startBottleThread(master3,mobileNum,lblbotVal,lblTimer,endcycleButton):
    global bottleCount,recycleStatus,gpioHandle,oprcycleCount
    print '\n Reading GPIO'
    settings.timerStatus = 0
    if gpioHandle is None:
        gpioHandle = pigpio.pi()
    print '\n gpioHandle is :', gpioHandle
    gpioHandle.set_mode(20, pigpio.INPUT)
    gpioHandle.set_mode(16, pigpio.INPUT)
    settings.performCycle = True 
    settings.LidStat = True
    cdTimer.screenTimer(lblTimer,20)
    oprcycleCount = 20

    Thr1 = threading.Thread(target=checkGpio,args=(lblTimer,master3))
    #Thr2 = threading.Thread(target=performGpio,args=(master3,))
    #Thr3 = threading.Thread(target=bottleThr,args=(lblbotVal,endcycleButton,master3))
    #Thr4 = threading.Thread(target=stopRoutine, args = (master3,optionSelect))
    Thr1.start()


#####################################################################################################
#                                                                                                   #
#                                                                                                   #
#                                   Choose Language                                                 #
#                                                                                                   #
#                                                                                                   #
#####################################################################################################


def recycleRoutine(root):
    global mainScreen,scrollTicker,lblTimer,endRecycleCount,timeCount,initScroller,gpioHandle
    
    mainScreen=root
    if initScroller is not None:
        root.after_cancel(initScroller)
    print '\n In recycling'
    root.withdraw()

    timeCount = 0
    endRecycleCount = False
    if gpioHandle is None:
        gpioHandle = pigpio.pi()
        gpioHandle.set_mode(22, pigpio.INPUT)
        gpioHandle.set_mode(25, pigpio.INPUT)

    master1 = tk.Toplevel()
    ws1 = master1.winfo_screenwidth() # width of the screen
    hs1 = master1.winfo_screenheight() # height of the screen

    coverPhoto = Image.open(imagesEnglish + "Screen2/" + "Background.jpg")
    coverPhoto = ImageTk.PhotoImage(coverPhoto)
    lblBackground = Label(master1,width=ws1,height=hs1, image=coverPhoto)
    lblBackground.photo = coverPhoto
    lblBackground.pack(fill=BOTH, expand = YES)
    #lblBackground.place(x=0,y=0)


    lblTimer = Label(lblBackground,width=100,height=2,font=('Times',20,'bold'),bg="white")
    lblTimer.place(x=1225,y=5)

    settings.timerStatus = 1
    cdTimer.screenTimer(lblTimer,20)

    backThr = master1.after(20000,lambda: backRoutine(master1,mainScreen))
    
    imgEnglish = Image.open(imagesEnglish + "Screen2/" +  "English.jpg")
    imgEnglish = imgEnglish.resize((460,145), PIL.Image.ANTIALIAS)
    imgEnglish = ImageTk.PhotoImage(imgEnglish)
    engButton = tk.Button(lblBackground,highlightthickness=0,bd=0,bg="#d61f36",borderwidth= 0,image=imgEnglish,command=lambda: winRecycling(master1,1,backThr))
    engButton.image = imgEnglish
    engButton.place(x=190,y=hs1-195)

    imgHindi = Image.open(imagesHindi + "Screen2/" +"Hindi.jpg")
    imgHindi = imgHindi.resize((465,145), PIL.Image.ANTIALIAS)
    imgHindi = ImageTk.PhotoImage(imgHindi)
    hindiButton = tk.Button(lblBackground,highlightthickness=0,bd=0,bg="#d61f36",borderwidth= 0,image=imgHindi,command=lambda: winRecycling(master1,2,backThr))
    hindiButton.image = imgHindi
    hindiButton.place(x=ws1-654,y=hs1-195)
    master1.attributes("-fullscreen", True)
    master1.config(width =ws1, height=hs1)
    master1.mainloop()

def closeLid():
    global endRecycleCount
    if endRecycleCount is True:
        print '\n Bypassing Lid '
        return 
    try:
        print '\n Closing Lid'
        operGpios(6)
        endRecycleCount = True
    except:
       print '\n Unable to Open the Lid' 


def endRecycling(master3,langOption):
    print '\n Ending Recycling'
    global mainScreen,mainScreen1,mobileNum, recycleStatus,driveConveyer,scrollTicker,endRecycleCount,gpioHandle
    recycleStatus = False
    driveConveyer = False
    settings.performCycle = False 
    if settings.LidStat is True:
        operGpios(6)
        gpioHandle.write(13,1)
        gpioHandle.write(26,1)
    settings.LidStat= False
    
    if settings.botCount == 0 :
        initVariables()
        backPrgm(master3,mainScreen)
        return
    else:
        if scrollTicker is not None:
            master3.after_cancel(scrollTicker)
        master3.destroy()
        master4 = tk.Toplevel()
        ws4 = master4.winfo_screenwidth() # width of the screen
        hs4 = master4.winfo_screenheight() # height of the screen

        if langOption == 1:
            coverPage = Image.open(imagesEnglish + "Screen7/" + "Background.jpg")
        else:  
            coverPage = Image.open(imagesHindi + "Screen7/" + "Background.jpg")

        coverPage = ImageTk.PhotoImage(coverPage)
        lblBackground = Label(master4,width=ws4,height=hs4, image=coverPage)
        lblBackground.photo = coverPage
        lblBackground.pack(fill=BOTH, expand = YES)

        lblValue = Label(lblBackground,font=('Times',80,'bold'),bg="#10ba4c",text=str(settings.botCount))
        lblValue.place(x=635,y= 408 )
        
        master4.attributes("-fullscreen", True)
        master4.config(width=ws4, height=hs4)
        master4.after(1000, lambda: getCouponlist(master4,mobileNum,settings.botCount))
        master4.mainloop()

def stopRoutine(scr1,optionSelect):
    global mainScreen,gpioHandle,recycleStatus,oprcycleCount
    """
    if oprcycleCount > 1:
        print '\n Continuing'
        #scr1.after(1000, lambda: stopRoutine(scr1,optionSelect))
    else:
    """
    recycleStatus=False
    if oprcycleCount <= 1:
        #settings.timerStatus = 0
        print '\n Closing Lid'
        operGpios(6)
        gpioHandle.write(13,1)
        gpioHandle.write(26,1)
        if settings.botCount == 0:
            print '\n Going on MainScreen without recycling bottles'
            settings.LidStat = False
            backPrgm(scr1,mainScreen) 
        elif settings.botCount >= 1 :
            print '\n Going on Next Screen after recycling bottles'
            try:
                endRecycling(scr1,optionSelect)
            except:
                pass
        print '\n Exiting Stop Routine'



def checkMobentry(master2,mobTxt,recycleButton):
    global mobileNum,timeCount,mainScreen,timeCount,mobEntry
    mobileNum = mobTxt.get('1.0',END).rstrip()
    mobEntry = None
    if len(mobileNum) != 10:
        mobEntry = master2.after(1000,lambda : checkMobentry(master2,mobTxt,recycleButton))
        if timeCount == 21:
            print '\n Cancelling Timer'
            master2.after_cancel(mobEntry)
            #mainScreen1.destroy()
            print '\n Going Back to Original Screen'
            endScreen(master2,mainScreen)
            timeCount = 0
        else:
            timeCount +=1 
    else:
        print '\n Got 10 digit mobile number'
        timeCount = 0
        recycleButton.config(state="normal")


def startRecycling(master2,mobTxt):
    global optionSelect,mobileNum,recycleStatus,mainScreen,LidStat,oprcycleCount
    recycleStatus = True
    LidStat = False
    print '\n In Start Recycle Loop'
     
    master2.destroy()
    master3 = tk.Toplevel()
    ws3 = master3.winfo_screenwidth() # width of the screen
    hs3 = master3.winfo_screenheight() # height of the screen

    master3.config(width =ws3, height=hs3)
    oprcycleCount = 20 
    if optionSelect == 1:
        coverPage = Image.open(imagesEnglish + "Screen5/" + "Background.jpg")
        imgEndcycle = Image.open(imagesEnglish + "Screen5/" +"endRecycle.jpg")
    else:
        coverPage = Image.open(imagesHindi + "Screen5/" + "Background.jpg")
        imgEndcycle = Image.open(imagesHindi + "Screen5/" +"endRecycle.jpg")

    coverPage = ImageTk.PhotoImage(coverPage)
    lbl3Background = Label(master3,width=ws3,height=hs3, image=coverPage)
    lbl3Background.photo = coverPage
    lbl3Background.pack(fill=BOTH, expand = YES)
   
    lblimgScroller = Label(lbl3Background,width=890,height=723,bg="white")
    lblimgScroller.place(x=0,y=0)

    labelTimer = Label(lbl3Background,width=100,height=4,bg="white")
    labelTimer.place(x=1225,y=5)

    lblbotVal = Label(lbl3Background,width=5,height=3,font=('Times','30','bold'),fg="black",bg="white",text="0")
    lblbotVal.place(x=ws3 - 200,y=100)
        
    #imgEndcycle = imgEndcycle.resize((500,150), PIL.Image.ANTIALIAS)
    imgEndcycle = ImageTk.PhotoImage(imgEndcycle)

    endcycleButton = tk.Button(master3,highlightthickness=0,bd=0,state=DISABLED,image=imgEndcycle,command=lambda: endRecycling(master3,optionSelect))
    endcycleButton.image = imgEndcycle
    #endcycleButton.place(x=865,y=595)
    endcycleButton.place(x=945,y=590)

    master3.attributes("-fullscreen", True)
    try:
        master3.after(250, lambda: operGpios(5))
    except:
        master3.after(250, lambda: operGpios(5))


    #master3.after(3000,cdTimer.screenTimer(labelTimer,20))
    #master3.after(1000, lambda: scrollingImg(master3,lblimgScroller))
    #master3.after(500, lambda: stopRoutine(master3,optionSelect))
    master3.after(1000,lambda : bottleThr(lblbotVal,endcycleButton,master3))
    master3.after(1000, lambda: startBottleThread(master3,mobileNum,lblbotVal,labelTimer,endcycleButton))
    master3.mainloop() 



#####################################################################################################
#                                                                                                   #
#                                                                                                   #
#                                                                                                   #
#                                                                                                   #
#                                                                                                   #
#####################################################################################################

def winRecycling(mainWindow1,langValue,timScr1):
    global mainScreen,optionSelect,scrollTicker
    optionSelect = langValue
    timeCount = 0
    print '\n Cancelling Timer'
    mainWindow1.after_cancel(timScr1)
    if optionSelect == 1:
        print '\n Language choosen is English'
    else:
        print '\n Language choosen is Hindi'
   
    mainWindow1.destroy()
    master2 = tk.Toplevel()
    ws2 = master2.winfo_screenwidth() # width of the screen
    hs2 = master2.winfo_screenheight() # height of the screen
    
    backgroundPhoto = Image.open(imagesEnglish + "Screen3/" + "Background.jpg")
    backgroundPhoto = ImageTk.PhotoImage(backgroundPhoto)
    lbl1Background = Label(master2,width=ws2,height=hs2, image=backgroundPhoto)
    lbl1Background.photo = backgroundPhoto
    lbl1Background.pack(fill=BOTH, expand = YES)

    #settings.timerStatus = 0
    
    lbTimer = Label(lbl1Background,width=100,height=2,font=('Times',20,'bold'),bg="white")
    lbTimer.place(x=1225,y=5)

    lblMob = Label(lbl1Background,font=('Times','22','bold'),bg="white", textvariable = "")
    lblMob.config(text="Enter 10 Digit Mobile Number")
    lblMob.place(x=10,y=10)
   
    #settings.timerStatus = 1 

    #cdTimer.screenTimer(lbTimer,20)

    mobTxtBox = tk.Text(lbl1Background,highlightthickness=0,bd=0,height=2,width=100,bg="white",font=('Vrinda',35,'bold'),relief=FLAT)
    mobTxtBox.place(x=550,y=10)
    
    keyFrame = Frame(lbl1Background, width=600, height = 600,bg="#FDFDF8")
    keyFrame.place(x=182,y=hs2 - 600)

    
    buttons = [
              ['1','2','3'],
              ['4','5','6'],
              ['7','8','9' ],
              ['Clr','0','Bk']
              ]
    i=0
    for r in range(4):
        for c in range(3):
            rImg = Image.open(imgButtons + keypadList[i] + ".jpg")
            newImg = ImageTk.PhotoImage(rImg)
            #button = tk.Button(keyFrame,font=('Vrinda','12','bold'),padx=20,pady=10,relief = RAISED,image=newImg, command = partial(buttonClicked, buttons[r][c],mobTxtBox))
            button = tk.Button(keyFrame,font=('Vrinda','15','bold'),highlightthickness=0,bd=0,image=newImg, command = partial(buttonClicked, buttons[r][c],mobTxtBox))
            button.image = newImg
            button.grid(row=r,column =c)
            i = i + 1
            keyFrame.update()

    if optionSelect == 1:
        recycleImg = Image.open(imagesEnglish + "Screen3/"+ "startRecycle.jpg")
        backImg = Image.open(imagesEnglish + "Screen3/"+ "Goback.jpg")
    else:
        recycleImg = Image.open(imagesHindi + "Screen3/" + "startRecycle.jpg")
        backImg = Image.open(imagesHindi + "Screen3/" + "Goback.jpg")
    
    #recycleImg = recycleImg.resize((420,175), PIL.Image.ANTIALIAS)
    recycleImg = ImageTk.PhotoImage(recycleImg)
    recycleButton = tk.Button(lbl1Background,highlightthickness=0,bd=0,bg="white",state=DISABLED,image=recycleImg,command=lambda: startRecycling(master2,mobTxtBox))
    recycleButton.image = recycleImg
    recycleButton.place(x=886,y = 320)

    #backImg = backImg.resize((420,175), PIL.Image.ANTIALIAS)
    backImg = ImageTk.PhotoImage(backImg)
    backButton = tk.Button(lbl1Background,highlightthickness=0,bd=0,bg="white",image=backImg,command=lambda: backRoutine(master2,mainScreen))
    backButton.image = backImg
    backButton.place(x=886,y= 450)

    master2.attributes("-fullscreen", True)
    master2.config(width =ws2, height=hs2)
    master2.after(1000,lambda: checkMobentry(master2,mobTxtBox,recycleButton))
    #master2.after(20000, lambda: backRoutine(master2,mainScreen1))
    master2.mainloop()


root = tk.Tk()

initscreenList = getfileList(initscreenPath)
initscreenList.sort()

print '\n initscreenList is :', initscreenList 

staticimgList = getfileList(staticImgPath)
staticimgList.sort()
print '\n staticimgList is :', staticimgList

# get screen width and height
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen

if gpioHandle is None:
    gpioHandle = pigpio.pi()
with open('/home/pi/Lidstat.txt', 'r') as myfile:
    data = myfile.read().replace('\n', '')
    if "Open" in data:
        operGpios(6)
        #gpioHandle.stop()
        #gpioHandle=None

print '\n ws is:', ws
print '\n hs is:', hs

labelVariable = StringVar()

Photo = Image.open(imgBackground + "Background.jpg")

idlePhoto = ImageTk.PhotoImage(Photo)
lblImg = Label(root,width=ws,height=hs, image=idlePhoto)
lblImg.photo = idlePhoto
lblImg.pack(fill=BOTH, expand = YES)

labelImg =  Label(lblImg,width=1366,height=645) 
#labelImg.pack(fill=BOTH, expand = YES)
labelImg.place(x=0,y= 0)

root.title(" Reverse Wending Machine ")

startImg = Image.open(imgBackground + "Start.jpg")
startImg = ImageTk.PhotoImage(startImg)
recycleButton= tk.Button(lblImg,image=startImg,highlightthickness=0,bd=0,command=lambda: recycleRoutine(root))
recycleButton.image = startImg
recycleButton.place(x=0,y= hs-120, width =ws, height = 120)

root.attributes("-fullscreen", True)
root.after(250,lambda : changeImg(labelImg,root))
root.config(width =ws, height=hs)
root.mainloop()

