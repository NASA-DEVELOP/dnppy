from Tkinter import *
import tkFileDialog
import Calender
import SciHub
import sys
import time
import os
from dnppy import download
from datetime import datetime as dt
import datetime
import tkMessageBox

class ImportTool:
    def __init__ (self, r):
        self.root = r
        
        self.file = ''
        self.lblFileDialog = Label()
        
        m1 = PanedWindow()
        m1.pack(fill=BOTH, expand = 1)
        m2 = PanedWindow(orient=VERTICAL)
        m1.add(m2)
        
        pndwinTop = PanedWindow(m2, orient=HORIZONTAL)
        m2.add(pndwinTop)
        
        self.frmTop = Frame(pndwinTop)
        self.frmTop.pack(side = TOP)
        
    def centerWindow(self):
        w = 450
        h = 275
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w)/2
        y = (sh - h)/2
        self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))
        
    #Creates the GUI window
    def setupWindow(self):
        self.root.title("Imagery Retrieval Tool")
        self.centerWindow()

    def importFile(self):
        dlg = tkFileDialog.askdirectory(initialdir='/', title='Select a location to save downloaded data.')
        if dlg:
            dirTxt.set(dlg)
            
    def firstDateSelect(self):
        calWin=Toplevel(self.root)        
        calWin.title('Select First Date')       
        w = 250
        h = 200                   
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w)/2
        y = (sh - h)/2       
        C = Calender.Calendar(calWin, firstweekday=Calender.calendar.SUNDAY)        
        C.pack()
        selBtn=Button(calWin, width=10, text='Select', command=lambda: self.select_Date1(calWin, C))
        selBtn.pack(side=BOTTOM)      
        calWin.geometry('%dx%d+%d+%d' % (w, h, x, y))       
        
    def secondDateSelect(self):
        calWin=Toplevel(self.root)        
        calWin.title('Select Second Date')       
        w = 250
        h = 200                   
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w)/2
        y = (sh - h)/2       
        C = Calender.Calendar(calWin, firstweekday=Calender.calendar.SUNDAY)        
        C.pack()
        selBtn=Button(calWin, width=10, text='Select', command=lambda: self.select_Date2(calWin, C))
        selBtn.pack(side=BOTTOM)         
        calWin.geometry('%dx%d+%d+%d' % (w, h, x, y))
        
    def about(self): 
        filewin = Toplevel(self.root)
        filewin.title("About")
        T = Message(filewin, text="NASA DEVELOP \nLaRC Summer 2015 Term \n \nWill Manion (Team Lead) \nAmy Ferguson \nKristen Noviello \nJordan Vaa \nCatelyn Quinn \nNicole MacDonald\n")
        T.pack()
        
        btnClose = Button(filewin, text="Close", command=filewin.destroy)
        btnClose.pack()    

    def select_Date1(self, root, cal):
        d=cal.selection
        global date1
        if d != None:
            date1Text.set(dt.date(d))
            date1=dt.date(d)
        root.destroy()
        
    def select_Date2(self, root, cal):
        d=cal.selection
        global date2
        if d != None:
            date2Text.set(dt.date(d))
            date2=dt.date(d)
        root.destroy()
     
    def run_click(self):
        if not os.path.exists('settings.cfg'):
            tkMessageBox.showerror(title='Config Error', message='No configuration file found\nSettings.cfg is missing.')
        elif date1 > date2:
            tkMessageBox.showerror(title='Invalid Date Range', message='Invalid Date Range\nPlease enter the earlier date first')
        else:
            dirStr=dirTxt.get()
            time=datetime.time()
            print 'the directory is: ' + dirStr
            if boolSent1.get():
                print 'Sent1 selected'
                SciHub.main(date1, date2, dirStr)
            if boolModis.get():
                download.fetch_MODIS('MYD09GA','005','h11v02',dirStr,dt.combine(date1,time),dt.combine(date2,time))
                download.fetch_MODIS('MOD09GA','005','h11v02',dirStr,dt.combine(date1,time),dt.combine(date2,time))
                download.fetch_MODIS('MYD09GA','005','h12v01',dirStr,dt.combine(date1,time),dt.combine(date2,time))
                download.fetch_MODIS('MOD09GA','005','h12v01',dirStr,dt.combine(date1,time),dt.combine(date2,time))
                download.fetch_MODIS('MYD09GA','005','h13v01',dirStr,dt.combine(date1,time),dt.combine(date2,time))
                download.fetch_MODIS('MOD09GA','005','h13v01',dirStr,dt.combine(date1,time),dt.combine(date2,time))
            if boolLandsat.get():
                self.landsatRetrieval(dirStr, time)
            if not boolSent1.get() and not boolModis.get() and not boolLandsat.get():
                tkMessageBox.showerror(title='No Platform Selected', message='Please select a platform to download imagery from')

    def landsatRetrieval(self, dirStr, time):
        largeArray = [[]]
    
        xV1=68
        xV2=69
        xV3=70
        xV4=71
    
        yV1=11
        yV2=10
        yV3=9
        yV4=8
    
        for i in range(0,19):         
            largeArray.append([xV1,yV1])
            xV1=xV1+1
    
            largeArray.append([xV2,yV2])
            xV2=xV2+1
    
            largeArray.append([xV3,yV3])
            xV3=xV3+1
    
            largeArray.append([xV4,yV4])
            xV4=xV4+1
    
            i=i+1
        del largeArray[0]
        download.fetch_Landsat8(largeArray, dt.combine(date1,time), dt.combine(date2,time), dirStr)

       
    def setupMenu(self):
        menuBar = Menu(self.root)
        
        #File Menu
        menuFile = Menu(menuBar, tearoff=0)
        menuFile.add_command(label="About", command=self.about)
        menuFile.add_command(label="Exit", command=self.root.quit)        
        menuBar.add_cascade(label="File", menu=menuFile)
    
        #configure menu to screen
        self.root.config(menu=menuBar)
        
    def panedWindow(self):
        self.imageIconCalender=PhotoImage(file='CalenderIcon.gif')
        
        #File Dialog box, - shows the selected file
        lblSaveDir=Label(self.frmTop, text="Output Directory:")
        lblSaveDir.grid(row=1, column=0, sticky=W)
        text1=('')
        dirTxt.set(text1)
        txtDirectory=Label(self.frmTop, width = 36, bg= "white", textvariable= dirTxt, relief = SUNKEN, justify = LEFT)
        txtDirectory.grid(row=1, column=1)        
        btnBrowse=Button(self.frmTop, text ='Browse',  width = 10, command=self.importFile)
        btnBrowse.grid(row=1, column=3)   
        
        #First Date box - shows beginning date to consider
        lblSpace1=Label(self.frmTop)
        lblSpace1.grid(row=2, column=0)
        lblFirstDate=Label(self.frmTop, text="First Date:")
        lblFirstDate.grid(row=3, column=0, sticky=W)
        text2=('yyyy-mm-dd')
        date1Text.set(text2)
        txtFirstDate=Label(self.frmTop, width = 36, bg= "white", textvariable= date1Text, relief = SUNKEN, justify = LEFT)
        txtFirstDate.grid(row=3, column=1)
        btnCalender1=Button(self.frmTop, image=self.imageIconCalender, command=self.firstDateSelect)
        btnCalender1.grid(row=3, column=3)
        
        #Second Date box - shows end date to consider
        lblSpace2=Label(self.frmTop)
        lblSpace2.grid(row=4, column=0)
        lblSecondDate=Label(self.frmTop, text="Last Date:")
        lblSecondDate.grid(row=5, column=0, sticky=W)
        text3=('yyyy-mm-dd')
        date2Text.set(text3)
        txtSecondDate=Label(self.frmTop, width = 36, textvariable=date2Text, bg= "white", relief = SUNKEN, justify = LEFT)
        txtSecondDate.grid(row=5, column=1)
        btnCalender2=Button(self.frmTop, image=self.imageIconCalender, command=self.secondDateSelect)
        btnCalender2.grid(row=5, column=3)
        
        #Separates file and date labels from checkboxes
        lblSpace3=Label(self.frmTop)
        lblSpace3.grid(row=6, column=0)
        lblPlatforms=Label(self.frmTop, text="Platforms to download:")
        lblPlatforms.grid(row=7, column=0, columnspan=2, sticky=W)
        
        #Sentinel 1 checkbox
        chkBtnSen1=Checkbutton(self.frmTop, text="Sentinel-1: SAR", variable=boolSent1)
        chkBtnSen1.grid(row=10, column=0, columnspan=2, sticky=W)
         
        #Modis Checkbox
        chkBtnModis=Checkbutton(self.frmTop, text="Aqua/Terra: MODIS", variable=boolModis)
        chkBtnModis.grid(row=11, column=0, columnspan=2, sticky=W)
         
        #Landsat Checkbox
        chkBtnLandSat=Checkbutton(self.frmTop, text="Landsat 8: OLI/TIRS", variable=boolLandsat)
        chkBtnLandSat.grid(row=12, column=0, columnspan=2, sticky=W)
        
        #Run Button
        btnRun=Button(self.frmTop, text='Run', command=self.run_click)
        btnRun.grid(row=13, column=1, sticky=S)
       
    def setupMainScreen(self):
        self.panedWindow()
    
def main():
    rt = Tk()
    program = ImportTool(rt)

    global dirTxt
    dirTxt=StringVar('')
    global date1Text
    date1Text=StringVar('')
    global date2Text
    date2Text=StringVar('')
    
    global date1
    date1=dt.date(dt.now())
    global date2
    date2=dt.date(dt.now())
    
    global boolSent1
    boolSent1=IntVar(0)
    global boolModis
    boolModis=IntVar(0)
    global boolLandsat
    boolLandsat=IntVar(0)   
    
    program.setupWindow()
    program.setupMenu()
    program.setupMainScreen()
        
    rt.mainloop()
    
if __name__ == "__main__":
    main()       
