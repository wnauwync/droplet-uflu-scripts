# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 17:08:02 2021

@author: wnauwync
"""

#Droplet GUI script

#Three windows: 
#1)    Directory selection
#2)    Parameter window
#3)    Analysis and plotting window



#######################################################
#                                                     #
#####                Library imports              #####
#                                                     #
#######################################################
import tkinter as tk
from scipy import ndimage
import os
from PIL import Image, ImageTk
from tkinter import messagebox
import pandas as pd
import numpy as np
#import skimage as skm
from skimage import io
from skimage import filters
import matplotlib
from matplotlib import pyplot as plt
from math import floor, ceil
import statistics
#from random import randint

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

matplotlib.use('TkAgg')


#######################################################

#💦

#######################################################
#                                                     #
#####              Directory selection            #####
#                                                     #
#######################################################
#Top class

#Initial screen --> set working dir to desired dir where all png files are found
#Allow multiple analyses --> have starting UI to select directory
#Droplets should go from left to right



class directorySelection:
    def __init__(self,parent,*args,**kwargs):
        self.parent = parent
        self.parent.iconphoto(False, tk.PhotoImage(file='C:/Users/wnauwync/Pictures/splashingsweat.png'))
        self.parent.title('dropTop')
        self.parent.geometry('400x215')
        
        #Create main frame and define lay-out of window  
        self.frame = tk.Frame(self.parent)
        self.frame.grid(row = 0, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W), padx = 10, pady = 10)
        self.frame2 = tk.Frame(self.parent)
        self.frame2.grid(row = 1, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W), padx = 100, pady = 5)
        
        
        # Tkinter variables
        self.filename = tk.StringVar()
        self.statusLabel = tk.StringVar()
        self.parent.selectedDir_success = tk.BooleanVar()
        self.parent.selectedDir_success.set(False)
        self.parent.plotNumber = 0
        
        #Add UI elements
        tk.Label(self.frame, text = 'Working directory').grid (row = 0, column = 0, sticky = (tk.W, tk.E))
        tk.Button(self.frame, text = 'Select directory:   ', command = self.selectDir).grid (row = 0, column = 1, sticky = (tk.W, tk.E))
        tk.Button(self.frame2, text = 'Start analyzing', command = self.startAnalysis).grid(row = 0,column = 0)
        self.succesDirLabel = tk.Label(self.frame2, textvariable=self.statusLabel)
        self.succesDirLabel.grid(row=0, column=1, sticky=(tk.W))
        self.succesDirLabel.grid_configure(padx = 10)
        
    
    # Open directory selection    
    def selectDir(self):
        self.dirName = tk.filedialog.askdirectory()
        if self.dirName == '':
            tk.messagebox.showerror('Error','Please specify a directory.')
            return
        else:
            self.parent.selectedDir_success.set(True)
            self.statusLabel.set('Directory selected.')
        
    def startAnalysis(self):
        if self.dirName == '':
            tk.messagebox.showerror('Error','Please specify a directory')
        elif len(os.listdir(self.dirName)) == 0:
            tk.messagebox.showerror('Error','Selected directory is empty.')
            return
        else:
            self.parameterWindow = parWindow(parent = self.parent, dirName = self.dirName)
  

#######################################################
#                                                     #
#####               Parameter window              #####
#                                                     #
#######################################################
#Perform analysis on 100 random subsequent droplets to optimize image analysis
#parameters
#add enterpress --> analyze
#add left and right key press
#Add go to droplet analysis

#initial values of image cut off and edge
# analyze --> allow reset button to be clicked
# reset --> show initial image and set success to false

#IF analysis = FALSE --> show images of raw data (move back and forth as well)
#The raw data should have the lines drawn on top
#IF analysis = TRUE --> show images of processed data

#change imageList depending on this value


#define processing area of image (reduce Sobel filter artefacts)
### add in entries for this: ABCD points of rectangle
### add in refresh button to reset config to initial

#define hitbox for droplet hits
###Draw line on left or right side with settings configed by user

## Add refresh button



class parWindow:
    def __init__(self,parent,dirName,*args,**kwargs):
        #define variables
        self.parent = parent
        self.dirName = dirName
        os.chdir(self.dirName)
                
        #open new window
        self.thisWindow = tk.Toplevel(self.parent)
        self.thisWindow.iconphoto(False, tk.PhotoImage(file='C:/Users/wnauwync/Pictures/splashingsweat.png'))
        self.initGUI()
        
    
    def initGUI(self):
        #add image
        self.myNewImage = Image.open(os.listdir(self.dirName)[0])
        self.myNewImage = self.myNewImage.resize((500,400), Image.ANTIALIAS)
        self.myNewImage = ImageTk.PhotoImage(self.myNewImage)        
        

        #Window lay out stuff
        self.thisWindow.title('dropTop: determine analysis parameters')
        self.thisWindow.geometry('1100x600')
        
        #add basic key functions
        self.thisWindow.bind("<Left>", lambda x: self.back())
        self.thisWindow.bind("<Right>", lambda x: self.forward())

        #GUI stuff
        ##Image frame
        self.imageFrame = tk.LabelFrame(self.thisWindow, text = 'Analysed images' )
        self.imageFrame.grid(row = 0, column = 0)
        
        #Define tkinter Variables
        self.imageAnalysisSuccess = tk.BooleanVar()
        self.imageAnalysisSuccess.set(False)
        self.imagePosition = 0
        
        #Image object
        
        self.imageCanvas = tk.Label(self.imageFrame, image = self.myNewImage)
        self.yCanvas = tk.Canvas(self.imageFrame, bg = 'white', height = 400, width = 40)
        self.xCanvas = tk.Canvas(self.imageFrame, bg = 'white', height = 40, width = 500)
        
        
        #Buttons
        self.buttonLeft = tk.Button(self.imageFrame,text = '<<', command = self.back)
        self.buttonRight = tk.Button(self.imageFrame,text = '>>', command = self.forward)
        self.buttonGo = tk.Button(self.imageFrame,text = 'Analyse data with these parameters', command = self.goToAnalysis)
        
        #Pack elements
        self.imageCanvas.grid(row = 0, column = 0, columnspan = 4)
        self.yCanvas.grid(row = 0, column = 5)
        self.xCanvas.grid(row = 1, column = 0, columnspan = 4)
        self.buttonLeft.grid(row = 2, column = 0, columnspan = 1)
        self.buttonRight.grid(row = 2, column = 3, columnspan = 1)
        self.buttonGo.grid(row = 5,column = 1, columnspan = 2)
        
        
        
        ##Parameter frame
        self.parameterFrame = tk.LabelFrame(self.thisWindow, text = "Parameters")
        self.parameterFrame.grid(row = 0, column = 1)
        
        #Define tkinter variables
        self.hiThrVar = tk.IntVar()
        self.imageStartVar = tk.IntVar()
        self.imageStopVar = tk.IntVar()
        self.xminVar = tk.IntVar()
        self.xmaxVar = tk.IntVar()
        self.yminVar = tk.IntVar()
        self.ymaxVar = tk.IntVar()
        self.edgemaxVar = tk.IntVar()
        self.edgeminVar = tk.IntVar()
        
        #Set tkinter variables
        self.hiThrVar.set(100)
        self.imageStartVar.set(100)
        self.imageStopVar.set(150)
        self.imageList = os.listdir(self.dirName)[self.imageStartVar.get():self.imageStopVar.get()]
        
        self.imageyMax = io.imread(self.imageList[0]).shape[0]
        self.imagexMax = io.imread(self.imageList[0]).shape[1]
        self.xminVar.set(0)
        self.xmaxVar.set(self.imagexMax)
        self.yminVar.set(0)
        self.ymaxVar.set(self.imageyMax)
        self.edgemaxVar.set(self.imageyMax)
        self.edgeminVar.set(0)
        
        
        
        
        #Entries
        self.threshEntry = tk.Entry(self.parameterFrame,textvariable = self.hiThrVar)
        self.xminEntry = tk.Entry(self.parameterFrame,textvariable = self.xminVar)
        self.xmaxEntry = tk.Entry(self.parameterFrame,textvariable = self.xmaxVar)
        self.yminEntry = tk.Entry(self.parameterFrame,textvariable = self.yminVar)
        self.ymaxEntry = tk.Entry(self.parameterFrame,textvariable = self.ymaxVar)
        self.edgemaxEntry = tk.Entry(self.parameterFrame,textvariable = self.edgemaxVar)
        self.edgeminEntry = tk.Entry(self.parameterFrame,textvariable = self.edgeminVar)
        
        #Buttons

        self.drawAreaButton = tk.Button(self.parameterFrame,text = 'Draw area', command = self.refreshCanvas)
        self.drawEdgeButton = tk.Button(self.parameterFrame,text = 'Draw edge', command = self.refreshCanvas)
        self.pickRandom = tk.Button(self.parameterFrame,text = 'Select', command = self.pickDrops)
        self.analyzeButton2 = tk.Button(self.parameterFrame, text = 'Process images', command = self.processImages)
        self.refreshButton = tk.Button(self.parameterFrame, text = 'Refresh', command = self.refreshGUI)
        
        #Pack elements and add labels
        
        tk.Label(self.parameterFrame,text = "Define image region to analyze:").grid(row = 0,column = 0,columnspan = 4, sticky = tk.W)
        tk.Label(self.parameterFrame,text = 'Xmin:').grid(row = 1, column = 0)
        self.xminEntry.grid(row = 1, column = 1)
        tk.Label(self.parameterFrame,text = 'Xmax:').grid(row = 1, column = 2)
        self.xmaxEntry.grid(row = 1, column = 3)
        tk.Label(self.parameterFrame,text = 'Ymin:').grid(row = 2, column = 0)
        self.yminEntry.grid(row = 2, column = 1)
        tk.Label(self.parameterFrame,text = 'Ymax:').grid(row = 2, column = 2)
        self.ymaxEntry.grid(row = 2, column = 3)
        self.drawAreaButton.grid(row = 3, column = 2, columnspan = 3, sticky = (tk.W, tk.E))
        tk.Label(self.parameterFrame,text = "Define edge for droplet detection:").grid(row = 4, column = 0, columnspan = 4, sticky = tk.W)
        tk.Label(self.parameterFrame,text = 'Emin:').grid(row = 5, column = 0)
        self.edgeminEntry.grid(row = 5, column = 1)        
        tk.Label(self.parameterFrame,text = 'Emax:').grid(row = 5, column = 2)
        self.edgemaxEntry.grid(row = 5, column = 3)
        self.drawEdgeButton.grid(row = 6, column = 2, columnspan = 3, sticky = (tk.W, tk.E))
        
        tk.Label(self.parameterFrame, text = 'Minimum brightness threshold:').grid(row = 7, column = 0,columnspan = 4, sticky = tk.W)
        tk.Label(self.parameterFrame, text= 'Threshold:').grid(row = 8, column = 2)
        self.threshEntry.grid(row = 8,column = 3)

                
        tk.Label(self.parameterFrame, text = 'Select different droplet sequence:').grid(row = 9, column = 0,columnspan = 4, sticky = tk.W)
        self.pickRandom.grid(row = 10,column = 2,columnspan = 3, sticky = (tk.W, tk.E))
        tk.Label(self.parameterFrame, text = 'Process images:').grid(row = 11, column = 0,columnspan = 4, sticky = tk.W)
        self.analyzeButton2.grid(row = 12, column = 2, columnspan = 3, sticky = (tk.W, tk.E))
        self.refreshButton.grid(row = 12, column = 0, columnspan = 2, sticky = (tk.W, tk.E))
        
        
        
        ###Draw extra elements on canvases
        #draw_line(x1,y1,x2,y2)
        #Region upper in y-axis
        self.yCanvas.create_line(0,floor(self.ymaxVar.get()/self.imageyMax*400),39,floor(self.ymaxVar.get()/self.imageyMax*400),width = 5,fill = "green")
        #Region lower in y-axis
        self.yCanvas.create_line(0,ceil(self.yminVar.get()/self.imageyMax*400),39,ceil(self.yminVar.get()/self.imageyMax*400),width = 5,fill = "red")
        #Edge detection in y-axis
        self.yCanvas.create_line(0,floor(self.edgemaxVar.get()/self.imageyMax*400),0,ceil(self.edgeminVar.get()/self.imageyMax*400),width = 10,fill = "blue")
        
        #Region lower in x-axis
        self.xCanvas.create_line(0,0,0,39, width = 5, fill = 'red')
        #Region upper in x-axis
        self.xCanvas.create_line(floor(self.xmaxVar.get()/self.imagexMax*500),0,floor(self.xmaxVar.get()/self.imagexMax*500),39,width = 5, fill = "green")
        
        
        
    def displayNewImage(self,myNewImage):
        #mynewimage is a Image.open object
        
        self.myNewImage = myNewImage
        self.myNewImage = self.myNewImage.resize((500,400), Image.ANTIALIAS)
        self.myNewImage = ImageTk.PhotoImage(self.myNewImage)
        
        #Set new image
        self.imageCanvas.grid_forget()
        self.imageCanvas = tk.Label(self.imageFrame,image = self.myNewImage)
        self.imageCanvas.grid(row = 0, column = 0, columnspan = 4)
    

    def forward(self):
        #get position from tkintervariable
        #set position again
        #refresh panel
        #make sure if end --> cannot go further
        
        if self.imagePosition < len(self.imageList)-1:
            self.imagePosition = self.imagePosition + 1
            

        newImage = self.imageList[self.imagePosition].split('.')[0]

        if self.imageAnalysisSuccess.get() == True:
            self.myNewImage = Image.open(self.dirName + '/procImages/' + newImage + '.png')
        elif self.imageAnalysisSuccess.get() == False:
            self.myNewImage = Image.open(self.dirName + '/'+ self.imageList[self.imagePosition])
            
        self.displayNewImage(self.myNewImage)
       
    def back(self):
        #get position from tkintervariable
        #set position again
        #refresh panel with next picture
        #make sure if end --> cannot go further
        
        if self.imagePosition > 0:
            self.imagePosition = self.imagePosition - 1
        
        newImage = self.imageList[self.imagePosition].split('.')[0]
        
       
        
        
        if self.imageAnalysisSuccess.get() == True:
            self.myNewImage = Image.open(self.dirName + '/procImages/' + newImage + '.png')
        elif self.imageAnalysisSuccess.get() == False:
            self.myNewImage = Image.open(self.dirName + '/' + self.imageList[self.imagePosition])
        
            
        self.displayNewImage(self.myNewImage)
                   
            
    def processImages(self):
        #get images to be analyzed from tkintervariables
        hiThr = self.hiThrVar.get()
        imageStart = self.imageStartVar.get()
        imageStop = self.imageStopVar.get()
        listFiles = os.listdir(self.dirName)[imageStart:imageStop]
        
        #Check if previous batch of pictures was made
        
        if 'procImages' not in os.listdir(self.dirName):
            os.mkdir('procImages/')
        elif len(os.listdir(self.dirName +'/procImages/'))>0:
            filesToRemove = os.listdir(self.dirName+'/procImages/')
            for i in filesToRemove:
                os.remove(self.dirName+'/procImages/'+i)

        
        for i in listFiles:
            imageProcessed = self.processImage(i,'demo',hiThr,self.xminVar.get(),self.xmaxVar.get(),self.yminVar.get(),self.ymaxVar.get())
            #if demo --> don't cut, replace by false
            #if not demo --> cut, don't replace by false
            name = i
            #save Images in directory processedImages (check if already there)
            imageProcessedNoExtension = name.split('.')[0]
            io.imsave('procImages/'+imageProcessedNoExtension+'.png', imageProcessed.astype(int))
        
        #Files are made and saved, now display first picture in canvas
        self.imagePosition = 0
        initialImage = listFiles[0].split('.')[0]
        self.myNewImage = Image.open(self.dirName + '/procImages/' + initialImage + '.png')
        
        self.displayNewImage(self.myNewImage)
        

        #Set imageList variable of class: 
        self.imageList = os.listdir(self.dirName+'/procImages/')
        self.imageAnalysisSuccess.set(True)

    def pickDrops(self):
        
        #reset to
        
        randomStart = np.random.randint(0,len(os.listdir(self.dirName))-51)
        self.imageStartVar.set(randomStart)
        self.imageStopVar.set(randomStart+50)
        self.imageAnalysisSuccess.set(False)
        self.imageList = os.listdir(self.dirName)[self.imageStartVar.get():self.imageStopVar.get()]
        self.imagePosition = 0
        
        
    def processImage(self,imageName,mode,hiThr,xmin,xmax,ymin,ymax):
        #perform edge detection, thresholding and closing of objects
        #add in region to be analyzed, add in edge to add from user input
        image = io.imread(imageName)
        
        xLen = image.shape[1]
        yLen = image.shape[0]
        
        image = image[ymin:ymax,xmin:xmax]
        image = self.sobelNormalizer(filters.sobel(image))
        image = image>hiThr

        #set complete side of image to True for shape closing
        image[:,image.shape[1]-1] = True
        image = ndimage.binary_fill_holes(image)
        
        if mode == 'demo':
            xminCut = np.zeros((image.shape[0],xmin),dtype = int)
            image = np.concatenate((xminCut,image),axis = 1)
            xmaxCut = np.zeros((image.shape[0],xLen-xmax),dtype = int)
            image = np.append(image,xmaxCut,axis = 1)
            yminCut = np.zeros((ymin,image.shape[1]),dtype = int)
            image = np.concatenate((yminCut,image),axis = 0)
            ymaxCut = np.zeros((yLen-ymax,image.shape[1]),dtype = int)
            image = np.append(image,ymaxCut,axis = 0)
            #imageOri = np.ones((200,150))
            #image = imageOri[ymin:ymax,xmin:xmax]
        
        image.astype(int)
        return image

    def sobelNormalizer(self,image):
        # 8-bit image, max = 255, min = 0
        # 0 = black
        # 255 = white
        #sometimes artefacts cause sobelNormalizer to maximize only the artefact
        
        scaleFactor = 255/image[0:len(image)-5].max()
        image = image*scaleFactor
        image = image.astype(int)
        return(image)
    
    def refreshCanvas(self):
        #delete lines from canvas and draw new lines with newly entered lines
        #if self.imageAnalysisSuccess.get() == False:
        self.yCanvas.delete('all')
        self.xCanvas.delete('all')
        
        if self.ymaxVar.get()<=self.imageyMax and self.yminVar.get()>=0:
            self.yCanvas.create_line(0,floor(self.ymaxVar.get()/self.imageyMax*400),39,floor(self.ymaxVar.get()/self.imageyMax*400),width = 5,fill = "green")
            self.yCanvas.create_line(0,ceil(self.yminVar.get()/self.imageyMax*400),39,ceil(self.yminVar.get()/self.imageyMax*400),width = 5,fill = "red")
        else:
            return
        if self.edgeminVar.get()>=0 and self.edgemaxVar.get()<=self.imageyMax:
            self.yCanvas.create_line(0,floor(self.edgemaxVar.get()/self.imageyMax*400),0,ceil(self.edgeminVar.get()/self.imageyMax*400),width = 10,fill = "blue")
        else:
            return            
        #Draw xcanvas
        if self.xmaxVar.get()<=self.imagexMax and self.xminVar.get()>=0:
            self.xCanvas.create_line(ceil(self.xminVar.get()/self.imagexMax*500),0,ceil(self.xminVar.get()/self.imagexMax*500),39, width = 5, fill = 'red')
            self.xCanvas.create_line(floor(self.xmaxVar.get()/self.imagexMax*500),0,floor(self.xmaxVar.get()/self.imagexMax*500),39,width = 5, fill = "green")
        else:
            return
    
    def refreshGUI(self):
        #workaround to avoid losing variables values when refreshing GUI
        #store variables
        tempXmin = self.xminVar.get()
        tempXmax = self.xmaxVar.get()
        tempYmin = self.yminVar.get()
        tempYmax = self.ymaxVar.get()
        tempEdgemin = self.edgeminVar.get()
        tempEdgemax = self.edgemaxVar.get()
        tempThr = self.hiThrVar.get()
        
        self.initGUI()
        
        #set variables again
        self.xminVar.set(tempXmin)
        self.xmaxVar.set(tempXmax)
        self.yminVar.set(tempYmin)
        self.ymaxVar.set(tempYmax)
        self.edgeminVar.set(tempEdgemin)
        self.edgemaxVar.set(tempEdgemax)
        self.hiThrVar.set(tempThr)
        #draw lines again        
        self.refreshCanvas()
        
        
    def goToAnalysis(self):
        #Pass all collected parameters to next window
        tempXmin = self.xminVar.get()
        tempXmax = self.xmaxVar.get()
        tempYmin = self.yminVar.get()
        tempYmax = self.ymaxVar.get()
        tempEdgemin = self.edgeminVar.get()
        tempEdgemax = self.edgemaxVar.get()
        tempThr = self.hiThrVar.get()
        
        parameterList = [tempXmin,tempXmax,tempYmin,tempYmax,tempEdgemin,tempEdgemax,tempThr]
        self.analysisWindow = analysisWindow(parent = self.parent, dirName = self.dirName, parameters = parameterList )


#######################################################
#                                                     #
#####                Plotting window              #####
#                                                     #
#######################################################
        
#Make sure title displays what data is being analysed
#make sure multiple analyses are allowed at the same time
#make sure the displayed data can be extracted in tsv files
#Add performance graph to window   


class analysisWindow:
    def __init__(self,parent,dirName,parameters,*args,**kwargs):
        self.parent = parent
        self.dirName = dirName
        self.parameterList = parameters
        os.chdir(self.dirName)
        
        
        self.xmin = self.parameterList[0]
        self.xmax = self.parameterList[1]
        self.ymin = self.parameterList[2]
        self.ymax = self.parameterList[3]
        self.edgemin = self.parameterList[4]
        self.edgemax = self.parameterList[5]
        self.hiThr = self.parameterList[6]
        
        self.thisWindow = tk.Toplevel(self.parent)
        self.thisWindow.iconphoto(False, tk.PhotoImage(file='C:/Users/wnauwync/Pictures/splashingsweat.png'))
        self.thisWindow.title('dropTop analysis:' + self.dirName)
        self.thisWindow.geometry('1000x860')
        
        
        #Create tkinter variables
        self.flowRateVar = tk.IntVar()
        self.specFileVar = tk.StringVar()
        self.frameRateVar = tk.IntVar()
        self.radioButVar = tk.IntVar()
        self.radioButVar.set(1)
        self.plotDataSuccess = tk.BooleanVar()
        self.plotDataSuccess.set(False)
        
        
        self.initGUI()
        

        
    def initGUI(self):

        self.plotCounter = -1
        
        #Create frame that holds UI for start of analysis
        #Pack frame as a starting point
        
        self.frameAnalysis = tk.LabelFrame(self.thisWindow,text = "Start analysis")
        self.frameAnalysis.grid(row = 0, column = 0)
        
        #Store certain elements in memory, pack others immediately
        
        self.flowRateEntry = tk.Entry(self.frameAnalysis,textvariable = self.flowRateVar)
        self.frameRateEntry = tk.Entry(self.frameAnalysis,textvariable = self.frameRateVar)
        self.analyzeButton1 = tk.Radiobutton(self.frameAnalysis, text = 'Analyze all', value = 1, variable = self.radioButVar)
        self.analyzeButton2 = tk.Radiobutton(self.frameAnalysis, text = 'Analyze latest',value = 2, variable = self.radioButVar)
        self.analyzeButton3 = tk.Radiobutton(self.frameAnalysis, text = 'Analyze starting from:',value = 3, variable = self.radioButVar)
        self.specFileEntry = tk.Entry(self.frameAnalysis, textvariable = self.specFileVar)
        self.analyzeButton = tk.Button(self.frameAnalysis, text = 'Analyze data',command = self.analyzeData)
        
        
        #Start packing
        tk.Label(self.frameAnalysis,text = 'Flow rate (uL/hr):').grid(row = 0,column = 0)
        self.flowRateEntry.grid(row = 1,column = 0)
        tk.Label(self.frameAnalysis, text = 'Frames per second (fps)').grid(row = 2, column = 0)
        self.frameRateEntry.grid(row = 3,column = 0)
        self.analyzeButton1.grid(row = 4,column = 0)
        self.analyzeButton2.grid(row = 5,column = 0)
        self.analyzeButton3.grid(row = 6,column = 0)
        self.specFileEntry.grid(row = 7,column = 0)
        self.analyzeButton.grid(row = 8,column = 0)
        
        
        #If button 3 is selected --> remove greyed out directory entry
        
        #If flow rate is not empty and (one of upper two buttons is selected or
        #if bottom radiobutton is selected and entry is entered ) Allow for analyze data button to be clicked
        
        
        
        ##Parameter frame
        self.parameterFrame = tk.LabelFrame(self.thisWindow, text = "Parameters")
        self.parameterFrame.grid(row = 1, column = 0)
        #Here user can alter parameters for analysis
        #But none yet identified o necessary, so keep it empty
        #Possible: pixels per um
        #Edge detection threshold
        #Channel detection interactivity
        #etc etc
        
        #Create variables necessary
        
        #self.pixPerUmVar = tk.StringVar()
        #self.framesVar = tk.StringVar()
        
        
        #Create elements
        
        #Pack elements
        tk.Label(self.parameterFrame, text = 'Your favorite analysis parameters').pack()
        
        
        
        
        
        
        ##Plot frames
        
        self.plotFrame = tk.LabelFrame(self.thisWindow, text = "Data plots")
        self.plotFrame.grid(row = 0, column = 1,rowspan = 3)
        
        
        ##Functions
        
    def analyzeData(self):
        #check flow rate entry, if none entered --> error
        #check analyze buttons, if none selected --> error
        self.picBatches = []
        self.picList = os.listdir(self.dirName)
        
        if 'procImages' in self.picList:
            self.picList.remove('procImages')
                
        
        dropData = pd.DataFrame([])
        dropPerformance = pd.DataFrame([])
        
        for i in self.picList:
            self.picBatches.append(i[0:4])
        
        self.picBatches = list(set(self.picBatches))
        self.picBatches.sort()
        
        #check for different states of GUI entries before continuing to analysis
        
        if not self.flowRateVar.get():
            messagebox.showerror('Error','Please enter a flow rate')
            return
        if not self.frameRateVar.get():
            messagebox.showerror('Error','Please enter a frame rate')
            return
        if self.flowRateVar.get() == 0:
            messagebox.showerror('Error','Please enter a non-zero flow rate')
            return
        if self.frameRateVar.get() == 0:
            messagebox.showerror('Error','Please enter a non-zero frame rate')
            return
        
        if self.radioButVar.get() == 1:
            self.picBatches = self.picBatches
            
        elif self.radioButVar.get() == 2:     
            self.picBatches = [str(self.picBatches[len(self.picBatches)-1])]
            
            #Analyze from entry
        elif self.radioButVar.get() == 3:
            if self.specFileVar.get() in self.picBatches:
                self.index = self.picBatches.index(self.specFileVar.get())
                self.picBatches = self.picBatches[self.index:len(self.picBatches)]
                #check if empty
            else:
                messagebox.showerror('Error','File batch not found')
                return
        count = -1
        curData = []
        for i in self.picBatches:
            #function needs flowrate, fps, dropBatch
            count = count + 1
            if count == 0:
                timeStart = 0
                dataHold = self.dropletDetector(i,self.flowRateVar.get(),self.frameRateVar.get(),timeStart,str(count))
                curData = dataHold['dropData']
                curPerformance = dataHold['performance']
            elif count > 0:
                prevData = curData
                timeStart = prevData.iloc[len(prevData)-1,2]
                dataHold = self.dropletDetector(i,self.flowRateVar.get(),self.frameRateVar.get(),timeStart,str(count))
                curData = dataHold['dropData']
                curPerformance = dataHold['performance']
                
                
            dropData = dropData.append(curData)
            dropPerformance = dropPerformance.append(curPerformance)
            
        #plot different columns in different plots
        #analysis performance (ones and zeroes)
        #droplet frequency, droplet size, spacing
        self.plotData({'dropData': dropData,
                       'performance': dropPerformance})
        
        

        
    def dropletDetector(self,picBatchName,flowRate,frameRate,timeStart,indexBatch):
        #first element of frequency array and last element of interdroplet distance are
        #replaced by averages of whole array for simplicity purposes
        
        matching = [s for s in os.listdir(self.dirName) if picBatchName in s]
        
        
        timeData = np.arange(len(matching))/frameRate*1000 #in milliseconds
        dropletPass = [] #function performance
    
        for i in matching:
            image = parWindow.processImage(self,i,'analysis',self.hiThr,self.xmin,self.xmax,self.ymin,self.ymax)
            #print(self.detectEdge(image,self.edgemin,self.edgemax))
            dropletPass.append(self.detectEdge(image,self.ymin,self.edgemin,self.edgemax))
            
        #print(dropletPass)

        newList = self.analyzePasses(dropletPass)
        #timePoints = timeData[dropletPass.index(False):dropletPass.index(False,len(dropletPass)-1)] #only select timepoins that are of importance for droplet counting
        dropStartTime = timeData[newList[0]]
        #print(dropStartTime)
        #dropStartTime = list(np.asarray(dropStartTime) + timeStart)
        dropStopTime = timeData[newList[1]]
        #print(dropStopTime)
        #dropStopTime = list(np.asarray(dropStopTime) + timeStart)
        
        droppassTime = dropStopTime-dropStartTime
        #interdropTime = start of second minus stop of first
        
        interdropTime = dropStartTime[1:len(dropStartTime)]-dropStopTime[0:len(dropStopTime)-1]
        #add in average value for last droplet
        interdropTime = np.append(interdropTime,statistics.mean(interdropTime))
        
        frequencyList = []
        dropVolume = []
        
        
        
        for i in np.arange(len(dropStartTime)-1):
            frequency = 1/(dropStartTime[i+1]-dropStartTime[i])*1000
            frequencyList.append(frequency) #from 1/ms to 1/s
            dropVolume.append(flowRate*1e6/3600/frequency) #flowrate in uL/hr to pL/s
        #add in average value for first droplet
        frequencyList.insert(0,statistics.mean(frequencyList))
        #add in average value for first droplet
        dropVolume.insert(0,statistics.mean(dropVolume))
        
        indexBatchList = np.repeat(indexBatch,len(droppassTime))
        
        #interdroplet distance is appointed to a certain droplet in order to be able to add it to a pandas dataframe
        #Index      dropStart       dropStop      drop size (ms)      interdroplet distance (ms)   frequency(Hz)   Droplet size (pL)
        
        dropData = pd.DataFrame({'index': list(indexBatchList),
                                 'dropStart_ms': list(dropStartTime + timeStart),
                                 'dropStop_ms': list(dropStopTime + timeStart),
                                 'dropSize_ms': list(droppassTime),
                                 'dropSpace_ms': list(interdropTime),
                                 'dropFreq_Hz': frequencyList,
                                 'dropVol_pL': dropVolume})
        analysisPerformance = pd.DataFrame({'time_ms': list(timeData + timeStart),
                                            'dropPass': dropletPass})
        
        
        
        return {'dropData': dropData,
                'performance': analysisPerformance}
    
        #Frequency first element = average of all droplets
        #Interdroplet distance last element = average of all droplets
        
    def analyzePasses(self,passList): 
        
        dropStart = []
        dropStop = []
        previousElement = False
        start = passList.index(False)
        
        #end = passList.index(False, len(passList)-1)
        end = len(passList)-1-passList[::-1].index(False)
        
        for i in np.arange(start,end+1,1):
            
            if passList[i] == True:
                if previousElement == False:
                    dropStart.append(i)
            if passList[i] == False:
                if previousElement == True:
                    dropStop.append(i)
            previousElement = passList[i]
        
        
        #filter out single or double frame droplets (false positives)
        #toRemove = []
        for i in np.arange(len(dropStart)):
            delta = dropStop[i]-dropStart[i]        
            if delta <= 3:
                dropStart[i] = False
                dropStop[i] = False
    
        dropStart = list(filter(None,dropStart))
        dropStop = list(filter(None,dropStop))
        
        #list with beginpoints of droplets
        #list with endpoints of droplets        
        
        return [dropStart,dropStop]
    
    
    def detectEdge(self,image,ymin,yminEdge,ymaxEdge):
        
        #scale detection zone
        
        #image[self.edgeminVar.get()-self.yminVar.get():self.edgemaxVar.get()-self.yminVar.get(),image.shape[1]-1] = True

        detectionZone = image[yminEdge-ymin:ymaxEdge-ymin,len(image[0])-2]
    
        if sum(detectionZone)>3:
            return True
        else:
            return False

    
    def sobelNormalizer(self,image):
        # 8-bit image, max = 255, min = 0
        # 0 = black
        # 255 = white
        #sometimes artefacts cause sobelNormalizer to maximize only the artefact
        
        scaleFactor = 255/image[0:len(image)-5].max()
        image = image*scaleFactor
        image = image.astype(int)
        return(image)
        
    def plotData(self,dataHolder):
        #plot data in foreseen canvases
        #interdroplet distance is appointed to a certain droplet in order to be able to add it to a pandas dataframe
        #Index      dropStart       dropStop      drop size (ms)      interdroplet distance (ms)   frequency(Hz)   Droplet size (pL)        
        
        data = dataHolder['dropData']
        performance = dataHolder['performance']
        
        self.plotCounter = self.plotCounter + 1
        
        self.fig1 = plt.Figure(figsize = (8,2),dpi = 100)
        self.fig2 = plt.Figure(figsize = (8,2),dpi = 100)
        self.fig3 = plt.Figure(figsize = (8,2),dpi = 100)
        self.fig4 = plt.Figure(figsize = (8,2),dpi = 100)
        
        if self.plotCounter > 0:
            self.figCanvas1.get_tk_widget().destroy()
            self.figCanvas2.get_tk_widget().destroy()
            self.figCanvas3.get_tk_widget().destroy()
            self.figCanvas4.get_tk_widget().destroy()
            
            
        self.figCanvas1 = FigureCanvasTkAgg(self.fig1,master = self.plotFrame)
        self.figCanvas2 = FigureCanvasTkAgg(self.fig2,master = self.plotFrame)
        self.figCanvas3 = FigureCanvasTkAgg(self.fig3,master = self.plotFrame)
        self.figCanvas4 = FigureCanvasTkAgg(self.fig4,master = self.plotFrame)

        self.figCanvas1.get_tk_widget().pack(side = tk.TOP, fill = tk.BOTH, expand = 1)
        self.figCanvas2.get_tk_widget().pack(side = tk.TOP, fill = tk.BOTH, expand = 1)
        self.figCanvas3.get_tk_widget().pack(side = tk.TOP, fill = tk.BOTH, expand = 1)    
        self.figCanvas4.get_tk_widget().pack(side = tk.TOP, fill = tk.BOTH, expand = 1)
                    
        self.ax1 = self.fig1.add_subplot(111)
        self.fig1.subplots_adjust(bottom=0.25)
        self.ax2 = self.fig2.add_subplot(111)
        self.fig2.subplots_adjust(bottom=0.25)
        self.ax3 = self.fig3.add_subplot(111)
        self.fig3.subplots_adjust(bottom=0.25)
        self.ax4 = self.fig4.add_subplot(111)
        self.fig4.subplots_adjust(bottom=0.25)


        self.ax1.set_xlabel('Time (ms)')
        self.ax1.set_ylabel('Frequency (Hz)')
        #self.ax1.set_title('Frequency (Hz) vs time (ms)')
        
        self.ax2.set_xlabel('Time (ms)')
        self.ax2.set_ylabel('Droplet size (pL)') 
        #self.ax2.set_title('Droplet size (pL) vs time (ms)')

        self.ax3.set_xlabel('Time (ms)')
        self.ax3.set_ylabel('Interdroplet spacing (ms)') 
        #self.ax3.set_title('Interdroplet spacing (ms) vs time (ms)')
        self.ax4.set_xlabel('Time (ms)')
        self.ax4.set_ylabel('Function performance') 


        self.ax1.plot(data['dropStart_ms'],data['dropFreq_Hz'])
        self.ax2.plot(data['dropStart_ms'],data['dropVol_pL'])
        self.ax3.plot(data['dropStart_ms'],data['dropSpace_ms'])
        self.ax4.plot(performance['time_ms'],performance['dropPass'])
        
        self.figCanvas1.draw()
        self.figCanvas2.draw()
        self.figCanvas3.draw()
        self.figCanvas4.draw()        



    def refreshGUI(self):
        self.initGUI()
        
        
root = tk.Tk()
root.option_add('*tearOff', tk.FALSE)
root.resizable(1, 1)
GUI = directorySelection(root)
root.mainloop()     
