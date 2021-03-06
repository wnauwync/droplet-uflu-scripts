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
from skimage import feature
#from skimage import filters
import matplotlib
from matplotlib import pyplot as plt
from math import floor, ceil
import statistics
import re
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
        #self.parent.iconphoto(False, tk.PhotoImage(file='C:/Users/wnauwync/Desktop/Repositories/droplet-uflu-scripts/dropTop/exe/splashingsweat.ico'))
        self.parent.iconbitmap('C:/Users/wnauwync/Desktop/Repositories/droplet-uflu-scripts/dropTop/exe/splashingsweat.ico')
        self.parent.title('dropTop: directory selection')
        self.parent.geometry('400x215')
        self.dirName = ''
        
        #Create main frame and define lay-out of window  
        self.frame = tk.LabelFrame(self.parent,text = 'Directory selection')
        self.frame.grid(row = 0, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W), padx = 5, pady = 5,ipadx = 92,ipady = 62)
        # self.frame2 = tk.Frame(self.parent)
        # self.frame2.grid(row = 1, column = 0, sticky = (tk.N, tk.E, tk.S, tk.W), padx = 100, pady = 5)
        
        
        # Tkinter variables
        self.filename = tk.StringVar()
        self.statusLabel = tk.StringVar()
        self.parent.selectedDir_success = tk.BooleanVar()
        self.parent.selectedDir_success.set(False)
        self.parent.plotNumber = 0
        
        #Add UI elements
        tk.Label(self.frame, text = 'Working directory:  ').grid (row = 0, column = 0, sticky = (tk.W, tk.E))
        tk.Button(self.frame, text = 'Select directory', command = self.selectDir).grid (row = 0, column = 1, sticky = (tk.W, tk.E))
        tk.Button(self.frame, text = 'Start analyzing', command = self.startAnalysis).grid(row = 1,column = 1, sticky = (tk.W, tk.E), pady = 5)
        self.succesDirLabel = tk.Label(self.frame, textvariable=self.statusLabel)
        self.succesDirLabel.grid(row=1, column=0, sticky=(tk.W))
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


class parWindow:
    def __init__(self,parent,dirName,*args,**kwargs):
        #define variables
        self.parent = parent
        self.dirName = dirName
        os.chdir(self.dirName)
                
        #open new window
        self.thisWindow = tk.Toplevel(self.parent)
        #self.thisWindow.iconphoto(False, tk.PhotoImage(file='C:/Users/wnauwync/Pictures/splashingsweat.png'))
        self.thisWindow.iconbitmap('C:/Users/wnauwync/Desktop/Repositories/droplet-uflu-scripts/dropTop/exe/splashingsweat.ico')
        self.initGUI()
        
    
    def initGUI(self):
        #add image
        self.myNewImage = Image.open(os.listdir(self.dirName)[10])
        self.myNewImage = self.myNewImage.resize((500,400), Image.ANTIALIAS)
        self.myNewImage = ImageTk.PhotoImage(self.myNewImage)        
        

        #Window lay out stuff
        self.thisWindow.title('dropTop: determine analysis parameters')
        self.thisWindow.geometry('892x575')
        
        #add basic key functionality
        self.thisWindow.bind("<Left>", lambda x: self.back())
        self.thisWindow.bind("<Right>", lambda x: self.forward())
        self.thisWindow.bind("<Enter>", lambda x: self.refreshCanvas())
        
        #GUI stuff
        
        #############
        ##Image frame
        self.imageFrame = tk.LabelFrame(self.thisWindow, text = 'Analysed images' )
        self.imageFrame.grid(row = 0, column = 0)
        
        #Define tkinter Variables
        self.imageAnalysisSuccess = tk.BooleanVar()
        self.dropCurStatusVar = tk.StringVar()
        
        #Set tkinter variables
        self.imageAnalysisSuccess.set(False)
        self.dropCurStatusVar.set('No analysis started')
        self.imagePosition = 0
        


        #Plotting objects
        self.imageCanvas = tk.Label(self.imageFrame, image = self.myNewImage)
        self.yCanvas = tk.Canvas(self.imageFrame, bg = 'white', height = 400, width = 40)
        self.xCanvas = tk.Canvas(self.imageFrame, bg = 'white', height = 40, width = 500)
        
        
        #Buttons
        self.buttonLeft = tk.Button(self.imageFrame,text = '<<', command = self.back)
        self.buttonRight = tk.Button(self.imageFrame,text = '>>', command = self.forward)
        self.buttonGo = tk.Button(self.imageFrame,text = 'Analyse data with these parameters', command = self.goToAnalysis)
        
        #Labels
        self.labelAnalysis= tk.Label(self.imageFrame,textvariable = self.dropCurStatusVar,font = ('Calibri',15))
        
        #Pack elements
        self.imageCanvas.grid(row = 0, column = 0, columnspan = 4)
        self.yCanvas.grid(row = 0, column = 5)
        self.xCanvas.grid(row = 1, column = 0, columnspan = 4)
        self.buttonLeft.grid(row = 2, column = 0, columnspan = 1)
        self.buttonRight.grid(row = 2, column = 3, columnspan = 1)
        self.buttonGo.grid(row = 5,column = 1, columnspan = 2)
        self.labelAnalysis.grid(row = 6,column = 0, columnspan = 5,sticky = (tk.W, tk.E))
        
        
        #############
        ##Parameter frame
        self.parameterFrame = tk.LabelFrame(self.thisWindow, text = "Parameters")
        self.parameterFrame.grid(row = 0, column = 1)
        
        #Define tkinter variables
        self.sigmaVar = tk.IntVar()
        self.imageStartVar = tk.IntVar()
        self.imageStopVar = tk.IntVar()
        self.xminVar = tk.IntVar()
        self.xmaxVar = tk.IntVar()
        self.yminVar = tk.IntVar()
        self.ymaxVar = tk.IntVar()
        self.nImagesVar = tk.IntVar()
        self.nImagesVar.set(50)
        
        #Set tkinter variables
        self.sigmaVar.set(1)
        self.imageStartVar.set(10)
        self.imageStopVar.set(self.imageStartVar.get()+self.nImagesVar.get())
        self.imageList = os.listdir(self.dirName)[self.imageStartVar.get():self.imageStopVar.get()]
        self.imageyMax = io.imread(self.imageList[0]).shape[0]
        self.imagexMax = io.imread(self.imageList[0]).shape[1]
        self.xminVar.set(0)
        self.xmaxVar.set(self.imagexMax)
        self.yminVar.set(0)
        self.ymaxVar.set(self.imageyMax)

        
        #Entries
        self.sigmaEntry = tk.Entry(self.parameterFrame,textvariable = self.sigmaVar)
        self.xminEntry = tk.Entry(self.parameterFrame,textvariable = self.xminVar)
        self.xmaxEntry = tk.Entry(self.parameterFrame,textvariable = self.xmaxVar)
        self.yminEntry = tk.Entry(self.parameterFrame,textvariable = self.yminVar)
        self.ymaxEntry = tk.Entry(self.parameterFrame,textvariable = self.ymaxVar)
        self.nImagesEntry = tk.Entry(self.parameterFrame,textvariable = self.nImagesVar)
        
        #Buttons
        self.drawAreaButton = tk.Button(self.parameterFrame,text = 'Draw area', command = self.refreshCanvas)
        self.pickRandom = tk.Button(self.parameterFrame,text = 'Select', command = self.pickDrops)
        self.analyzeButton2 = tk.Button(self.parameterFrame, text = 'Process images', command = self.processBatch)
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
        tk.Label(self.parameterFrame,text = "Define amount of droplets to show:").grid(row = 4, column = 0, columnspan = 4, sticky = tk.W)
        tk.Label(self.parameterFrame,text = 'nDrops:').grid(row = 5, column = 2)
        self.nImagesEntry.grid(row = 5, column = 3)
        
        tk.Label(self.parameterFrame, text = 'Set sigma for Canny Gaussian filter:').grid(row = 7, column = 0,columnspan = 4, sticky = tk.W)
        tk.Label(self.parameterFrame, text= 'Sigma:').grid(row = 8, column = 2)
        self.sigmaEntry.grid(row = 8,column = 3)

                
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
    
    def refreshImage(self,myNewImage):
        
        newImage = self.imageList[self.imagePosition].split('.')[0]
        if self.imageAnalysisSuccess.get() == True:
            self.myNewImage = Image.open(self.dirName + '/procImages/' + newImage + '.png')
            self.myNewEdge = io.imread(self.dirName + '/procImages/' + newImage + '.png')
            self.detectRipple(self.myNewEdge)
        elif self.imageAnalysisSuccess.get() == False:
            self.myNewImage = Image.open(self.dirName + '/' + self.imageList[self.imagePosition])
        
        self.displayNewImage(self.myNewImage)
        
        
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
            self.myNewEdge = io.imread(self.dirName + '/procImages/' + newImage + '.png')
            self.detectRipple(self.myNewEdge)
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
            self.myNewEdge = io.imread(self.dirName + '/procImages/' + newImage + '.png')
            self.detectRipple(self.myNewEdge)
        elif self.imageAnalysisSuccess.get() == False:
            self.myNewImage = Image.open(self.dirName + '/' + self.imageList[self.imagePosition])
        
            
        self.displayNewImage(self.myNewImage)
                   
            
    def processBatch(self):
        #get images to be analyzed from tkintervariables
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
            imageProcessed = self.processImage(i,'demo',self.sigmaVar.get(),self.xminVar.get(),self.xmaxVar.get(),self.yminVar.get(),self.ymaxVar.get())
            #if demo --> don't cut, replace by false
            #if not demo --> cut, don't replace by false
            name = i
            #save Images in directory processedImages (check if already there)
            imageProcessedNoExtension = name.split('.')[0]
            io.imsave('procImages/'+imageProcessedNoExtension+'.png', imageProcessed.astype(int),check_contrast = False)
        
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
        
        randomStart = np.random.randint(0,len(os.listdir(self.dirName))-201)
        self.imageStartVar.set(randomStart)
        self.imageStopVar.set(randomStart+self.nImagesVar.get())
        self.imageAnalysisSuccess.set(False)
        self.imageList = os.listdir(self.dirName)[self.imageStartVar.get():self.imageStopVar.get()]
        self.imagePosition = 0
        self.refreshImage(self.myNewImage)
        
        
    def processImage(self,imageName,mode,sigmaInput,xmin,xmax,ymin,ymax):
        #perform Canny edge detection with sigma input from user
        image = io.imread(imageName)
        
        xLen = image.shape[1]
        yLen = image.shape[0]
        
        image = image[ymin:ymax,xmin:xmax]
        image = feature.canny(image,sigma = sigmaInput)
        
        
        if mode == 'demo':
            xminCut = np.zeros((image.shape[0],xmin),dtype = int)
            image = np.concatenate((xminCut,image),axis = 1)
            xmaxCut = np.zeros((image.shape[0],xLen-xmax),dtype = int)
            image = np.append(image,xmaxCut,axis = 1)
            yminCut = np.zeros((ymin,image.shape[1]),dtype = int)
            image = np.concatenate((yminCut,image),axis = 0)
            ymaxCut = np.zeros((yLen-ymax,image.shape[1]),dtype = int)
            image = np.append(image,ymaxCut,axis = 0)

    
        image.astype(int)
        return image

    def detectRipple(self,edgeImage):
        #images that get input are integer images with 0 and 255 values
        edgeImage = edgeImage>100
        if self.imageAnalysisSuccess.get() == True:
            #processed image with edges is read
            xwhereTrue = np.where(np.any(edgeImage,axis = 0) == True)[0]
            if len(xwhereTrue>2):
            #x axis (columns) used to determine
                xfirstTrue = xwhereTrue[0]
                xlastTrue = xwhereTrue[len(xwhereTrue)-1]
                
                firstTrue = np.where(edgeImage[:,xfirstTrue] == True)[0]
                yfirstTrue = firstTrue[0]
                
                lastTrue = np.where(edgeImage[:,xlastTrue] == True)[0]
                ylastTrue = lastTrue[0]
            
            
                if yfirstTrue < ylastTrue:
                    self.dropCurStatusVar.set('Start of droplet')
                elif yfirstTrue > ylastTrue:
                    self.dropCurStatusVar.set('End of droplet')
                else:
                    #if equal indices are found there are probably double edges
                    #that are messing with the analysis, add in extra
                    #if statements to deal with these
                    if len(firstTrue)>1:
                        yfirstTrue = firstTrue[len(firstTrue)-1]
                        if yfirstTrue < ylastTrue:
                            self.dropCurStatusVar.set('Start of droplet')
                        elif yfirstTrue > ylastTrue:
                            self.dropCurStatusVar.set('End of droplet') 
                        else:
                            self.dropCurStatusVar.set('No clear edge')
                    if len(lastTrue)>1:
                        ylastTrue = lastTrue[len(lastTrue)-1]
                        if yfirstTrue < ylastTrue:
                            self.dropCurStatusVar.set('Start of droplet')
                        elif yfirstTrue > ylastTrue:
                            self.dropCurStatusVar.set('End of droplet') 
                        else:
                            self.dropCurStatusVar.set('No clear edge')
            else:
                self.dropCurStatusVar.set('No clear edge')
        else:
            self.dropCurStatusVar.set('No analysis started')

                
    
    def refreshCanvas(self):
        #delete lines from canvas and draw new lines with newly entered lines
        self.yCanvas.delete('all')
        self.xCanvas.delete('all')
        
        if self.ymaxVar.get()<=self.imageyMax and self.yminVar.get()>=0:
            self.yCanvas.create_line(0,floor(self.ymaxVar.get()/self.imageyMax*400),39,floor(self.ymaxVar.get()/self.imageyMax*400),width = 5,fill = "green")
            self.yCanvas.create_line(0,ceil(self.yminVar.get()/self.imageyMax*400),39,ceil(self.yminVar.get()/self.imageyMax*400),width = 5,fill = "red")
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
        tempnImagesVar = self.nImagesVar.get()
        tempSigma = self.sigmaVar.get()
        
        self.initGUI()
        #set variables again
        self.xminVar.set(tempXmin)
        self.xmaxVar.set(tempXmax)
        self.yminVar.set(tempYmin)
        self.ymaxVar.set(tempYmax)
        self.nImagesVar.set(tempnImagesVar)
        self.sigmaVar.set(tempSigma)
        #draw lines again        
        self.refreshCanvas()
        
        
    def goToAnalysis(self):
        #Pass all collected parameters to next window
        tempXmin = self.xminVar.get()
        tempXmax = self.xmaxVar.get()
        tempYmin = self.yminVar.get()
        tempYmax = self.ymaxVar.get()
        tempSigma = self.sigmaVar.get()
        
        parameterList = [tempXmin,tempXmax,tempYmin,tempYmax,tempSigma]
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
        self.sigma = self.parameterList[4]
        
        self.thisWindow = tk.Toplevel(self.parent)
        #self.thisWindow.iconphoto(False, tk.PhotoImage(file='C:/Users/wnauwync/Pictures/splashingsweat.png'))
        self.thisWindow.iconbitmap('C:/Users/wnauwync/Desktop/Repositories/droplet-uflu-scripts/dropTop/exe/splashingsweat.ico')
        self.thisWindow.title('dropTop analysis: ' + self.dirName)
        self.thisWindow.geometry('917x957')
        
        

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
        
        #Bind basic functionalities to window
        self.thisWindow.bind("<Return>", lambda x: self.analyzeData())
        
        
        
        #Store certain elements in memory, pack others immediately
        
        self.flowRateEntry = tk.Entry(self.frameAnalysis,textvariable = self.flowRateVar)
        self.frameRateEntry = tk.Entry(self.frameAnalysis,textvariable = self.frameRateVar)
        self.analyzeButton1 = tk.Radiobutton(self.frameAnalysis, text = 'Analyze all', value = 1, variable = self.radioButVar)
        self.analyzeButton2 = tk.Radiobutton(self.frameAnalysis, text = 'Analyze latest',value = 2, variable = self.radioButVar)
        self.analyzeButton3 = tk.Radiobutton(self.frameAnalysis, text = 'Analyze specific batches:',value = 3, variable = self.radioButVar)
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
        
        ##Parameter frame
        self.parameterFrame = tk.LabelFrame(self.thisWindow, text = "Parameters")
        self.parameterFrame.grid(row = 1, column = 0)
        #Here user can alter parameters for analysis
        #But none yet identified o necessary, so keep it empty
        #Possible: pixels per um
        #Channel detection interactivity
        #etc etc
        
        #Create variables necessary
        
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
        picBatches = []
        self.picList = os.listdir(self.dirName)
        
        if 'procImages' in self.picList:
            self.picList.remove('procImages')
                
        
        dropData = pd.DataFrame([])
        dropPerformance = pd.DataFrame([])
        
        for i in self.picList:
            picBatches.append(i[0:4])
        
        picBatches = list(set(picBatches))
        picBatches.sort()
        
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
            self.picBatches = picBatches
            
        elif self.radioButVar.get() == 2:     
            self.picBatches = [str(picBatches[len(picBatches)-1])]
            
        elif self.radioButVar.get() == 3:
            string = self.specFileVar.get()
            index = []
            entryContent = self.splitEntry(string,picBatches)
            seps = entryContent[0]
            files = entryContent[1]
            if len(seps)>2:
                messagebox.showerror('Error', 'Please enter only one of following separator signs (:,)')
                return
            else:
                if ',' in seps:
                    for i in files:
                        if i in picBatches:
                            index.append(picBatches.index(i))
                        else:
                            messagebox.showerror('Error', 'File batch not found')
                            return
                    
                    self.picBatches = list(np.array(picBatches)[index])
                    
                    
                    
                elif ':' in seps:
                    for i in files:
                        if i in picBatches:
                            index.append(picBatches.index(i))
                        else:
                            messagebox.showerror('Error', 'File batch not found')
                            return
                    self.picBatches = picBatches[index[0]:index[1]]
                    
                else:
                    messagebox.showerror('Error', 'Please enter only one of following separator signs (:,)')
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
        
    def splitEntry(self,string,picBatches):
        #give all separators, transfor last to len etc
        files = []
        seps = []
        string.replace(" ","")
        entryElements = re.split('(\W)',string)
        count = -1
        for i in entryElements:
            count += 1
            if count%2 == 0:
                files.append(i)
            else:
                seps.append(i)

        if 'last' in files:
            index = files.index('last')
            files[index] = picBatches[len(picBatches)-1]
        
        return [seps,files]
        
        
    def dropletDetector(self,picBatchName,flowRate,frameRate,timeStart,indexBatch):
        #first element of frequency array and last element of interdroplet distance are
        #replaced by averages of whole array for simplicity purposes
        
        matching = [s for s in os.listdir(self.dirName) if picBatchName in s]
        timeData = np.arange(len(matching))/frameRate*1000 #in milliseconds
        dropletPass = [] #function performance
    
        for i in matching:
            image = parWindow.processImage(self,i,'analysis',self.sigma,self.xmin,self.xmax,self.ymin,self.ymax)
            dropletPass.append(self.detectEdge(image))
            
        passList = self.healVector(dropletPass)
        newList = self.analyzePasses(passList)
        
        dropStartTime = timeData[newList[0]]
        dropStopTime = timeData[newList[1]]
        indexBatchList = np.repeat(indexBatch,len(dropStartTime))
        
        
        #Catch errors caused by erroneously detected start times and stop times
        if len(dropStartTime) != len(dropStopTime):
            #If IndexError is detected, add in 0 Hz Frequency, 1 dropVolume,
            #2 droppassTime, 3 interdropTime
            frequencyList = np.zeros(len(dropStartTime))
            dropVolume = np.ones(len(dropStartTime))
            droppassTime = np.ones(len(dropStartTime))*2
            interdropTime = np.ones(len(dropStartTime))*3
            dropData = pd.DataFrame({'index': list(indexBatchList),
                                 'dropStart_ms': list(frequencyList),
                                 'dropStop_ms': list(frequencyList),
                                 'dropSize_ms': list(droppassTime),
                                 'dropSpace_ms': list(interdropTime),
                                 'dropFreq_Hz': list(frequencyList),
                                 'dropVol_pL': list(dropVolume)})
            analysisPerformance = pd.DataFrame({'time_ms': list(timeData + timeStart),
                                            'dropPass': dropletPass,
                                            'dropProc': passList})


        elif len(dropStartTime)>1 :
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
                                                'dropPass': dropletPass,
                                                'dropProc': passList})
            
            
        else:
            messagebox.showerror('Error', 'Analysis failed')
            return
            
            
        return {'dropData': dropData,
                'performance': analysisPerformance}
    
        #Frequency first element = average of all droplets
        #Interdroplet distance last element = average of all droplets
        
    def analyzePasses(self,passList):         
        dropStart = []
        dropStop = []
        previousElement = 0
        start = passList.index(1)
        
        #[::-1] reverses a list!
        try:
            end = len(passList)-1-passList[::-1].index(-1)
        except ValueError:
            dropStart = np.arange(0,20,2)
            dropStop = np.arange(1,20,2)
        else:
            #include direct transitions between two edges but increases chance
            #for false positive edge detection, remove this
            
            for i in np.arange(start,end+1,1):
                
                if passList[i] == 1:
                    if previousElement == 0 or previousElement == -1:
                        dropStart.append(i)
                if passList[i] == -1:
                    if previousElement == 0 or previousElement == 1:
                        dropStop.append(i)
                previousElement = passList[i]
        
        return [dropStart,dropStop]
        
        
    def collapseVector(self,passList):
        #this function reduces a passList (vector of -1,0 and 1) to a description
        #of the vector in two different vectors (ID and length)1,1,1, ==> ID [1] and length [3] 
        #0,0,0,1,1,0,-1,-1 will be turned into ID [0,1,0,-1] and length [3,2,1,2])
        
        
        i = 0
        islandIDList = []
        islandLengthList = []
        islandLength = 1

        
        while i < len(passList)-1:
            i = i + 1
            curVal = passList[i]
            preVal = passList[i-1]
            islandID = preVal
            
            if curVal == preVal:
                islandLength = islandLength + 1
                islandID = curVal
            else:
                islandIDList.append(islandID)
                islandLengthList.append(islandLength)
                islandLength = 1
        islandIDList.append(islandID)
        islandLengthList.append(islandLength)
            
        return [islandIDList,islandLengthList]

    def extractVector(self,islandIDList,islandLengthList):
        #this function does the inverse of extractVector, it extracts a vector
        #from a length vector and an IDvector
        
        passList = []
        
        if len(islandIDList) == len(islandLengthList):
            for i in np.arange(len(islandIDList)):
                elements = [islandIDList[i]] * islandLengthList[i]
                passList.extend(elements)
            return passList
        
        else:
            messagebox.showerror('Error','Droplet data cannot be analyzed due to unexpected droplet pattern, alter sigma or region of analysis.')
            return

    def healVector(self,passList):
        #Problem: sometimes double start or double endings are detected in the
        #droplet images while in reality there are none.
        #This throws off the analysis.
        #Here a method is introduced that fixes these false positives based 
        #on the vector environment and predicted droplet pass pattern
        
        #iterative process: 
           # 0)find anchor of three matching patterns with no singlets
           # 1)from start of vector, go forward until no match with predicted
           #droplet pass pattern (0,-1,0,1)perform healing (alter based on pattern prediction)
           # extractVector and collapse vector again
           # 2) go to anchor, go forward until no match, perform healin
        
        
        resultList = self.collapseVector(passList)
        islandIDList = resultList[0]
        islandLengthList = resultList[1]
        
        #0)correct singlets based on environment 
        #(just convert to smallest neighbouring island)
        
        for i in np.arange(1,len(islandIDList)-1):
            if islandLengthList[i] == 1:
                #determine index through smallest neighbouring island
                if islandLengthList[i+1] >= islandLengthList[i-1]:
                    islandIDList[i] = islandIDList[i-1]
                elif islandLengthList[i+1] < islandLengthList[i-1]:
                    islandIDList[i] = islandIDList[i+1]
                        
        newPassList = self.extractVector(islandIDList,islandLengthList)
        resultList = self.collapseVector(newPassList)
        islandIDList = resultList[0]
        islandLengthList = resultList[1]
        
        #1) find anchorpoint
        patternHeal = [0,-1,0,1] #data will always show this pattern
        match = False
        anchor = -1
        
        while match == False and anchor < len(islandIDList)-13:
            anchor = anchor + 1
            
            if islandIDList[anchor:anchor+12] == patternHeal * 3 and 1 not in islandLengthList[anchor:anchor+12]:
                match = True
        
        if match == False:
            messagebox.showerror('Error','Could not find an anchor point')
            
        #start adjusting pattern
        count = 0
        #keep adjusting until pattern is complete
        for i in np.arange(1,len(islandIDList)-1):
            index = (i - anchor - count) % 4
            
            if islandIDList[i] != patternHeal[index] and islandIDList[i] != 0:
                count = count + 1
                if islandIDList[i-1] == islandIDList[i+1]:
                    islandIDList[i] = islandIDList[i-1]
                elif islandLengthList[i+1] >= islandLengthList[i-1]:
                    islandIDList[i] = islandIDList[i-1]
                elif islandLengthList[i+1] < islandLengthList[i-1]:
                    islandIDList[i] = islandIDList[i+1]
                    
                    
                    
        newPassList = self.extractVector(islandIDList,islandLengthList)

        return newPassList

        
    
    def detectEdge(self,edgeImage):
        #almost same as detectRipple, but introduced in this class under
        #detectEdge
        #0 == no edge visible in picture
        #1 == front edge visible in picture
        #-1 == back edge visible in picture
        
        #edgeImage = edgeImage>100
        #processed image with edges is read
        edgeCur = 0
        xwhereTrue = np.where(np.any(edgeImage,axis = 0) == True)[0]
        if len(xwhereTrue>2):
        #x axis (columns) used to determine
            xfirstTrue = xwhereTrue[0]
            xlastTrue = xwhereTrue[len(xwhereTrue)-1]
            
            firstTrue = np.where(edgeImage[:,xfirstTrue] == True)[0]
            yfirstTrue = firstTrue[0]
            
            lastTrue = np.where(edgeImage[:,xlastTrue] == True)[0]
            ylastTrue = lastTrue[0]
        
        
            if yfirstTrue < ylastTrue:
                edgeCur = 1
            elif yfirstTrue > ylastTrue:
                edgeCur = -1
            else:
                #if equal indices are found there are probably double edges
                #that are messing with the analysis, add in extra
                #if statements to deal with these
                if len(firstTrue)>1:
                    yfirstTrue = firstTrue[len(firstTrue)-1]
                    if yfirstTrue < ylastTrue:
                        edgeCur = 1
                    elif yfirstTrue > ylastTrue:
                        edgeCur = -1
                    else:
                        edgeCur = 0
                if len(lastTrue)>1:
                    ylastTrue = lastTrue[len(lastTrue)-1]
                    if yfirstTrue < ylastTrue:
                        edgeCur = 1
                    elif yfirstTrue > ylastTrue:
                        edgeCur = -1
                    else:
                        edgeCur = 0
        else:
            edgeCur = 0
            
        return edgeCur

        
    def plotData(self,dataHolder):
        #plot data in foreseen canvases
        #interdroplet distance is appointed to a certain droplet in order to be able to add it to a pandas dataframe
        #Index      dropStart       dropStop      drop size (ms)      interdroplet distance (ms)   frequency(Hz)   Droplet size (pL)        
        global dropDataglobal
        
        dropData = dataHolder['dropData']
        performance = dataHolder['performance']
        dropDataglobal = dropData
        
        self.plotCounter = self.plotCounter + 1
        
        self.fig1 = plt.Figure(figsize = (8,2),dpi = 90)
        self.fig2 = plt.Figure(figsize = (8,2),dpi = 90)
        self.fig3 = plt.Figure(figsize = (8,2),dpi = 90)
        self.fig4 = plt.Figure(figsize = (8,2),dpi = 90)
        self.fig5 = plt.Figure(figsize = (8,2),dpi = 90)
        
        if self.plotCounter > 0:
            self.figCanvas1.get_tk_widget().destroy()
            self.figCanvas2.get_tk_widget().destroy()
            self.figCanvas3.get_tk_widget().destroy()
            self.figCanvas4.get_tk_widget().destroy()
            self.figCanvas5.get_tk_widget().destroy()
            
            
        self.figCanvas1 = FigureCanvasTkAgg(self.fig1,master = self.plotFrame)
        self.figCanvas2 = FigureCanvasTkAgg(self.fig2,master = self.plotFrame)
        self.figCanvas3 = FigureCanvasTkAgg(self.fig3,master = self.plotFrame)
        self.figCanvas4 = FigureCanvasTkAgg(self.fig4,master = self.plotFrame)
        self.figCanvas5 = FigureCanvasTkAgg(self.fig5,master = self.plotFrame)

        
        self.figCanvas1.get_tk_widget().grid(row = 0,column = 0)
        self.figCanvas2.get_tk_widget().grid(row = 1,column = 0)
        self.figCanvas3.get_tk_widget().grid(row = 2,column = 0)
        self.figCanvas4.get_tk_widget().grid(row = 3,column = 0)
        self.figCanvas5.get_tk_widget().grid(row = 4,column = 0)
        
                    
        self.ax1 = self.fig1.add_subplot(111)
        self.fig1.subplots_adjust(bottom=0.25)
        self.ax2 = self.fig2.add_subplot(111)
        self.fig2.subplots_adjust(bottom=0.25)
        self.ax3 = self.fig3.add_subplot(111)
        self.fig3.subplots_adjust(bottom=0.25)
        self.ax4 = self.fig4.add_subplot(111)
        self.fig4.subplots_adjust(bottom=0.25)
        self.ax5 = self.fig5.add_subplot(111)
        self.fig5.subplots_adjust(bottom=0.25)

        self.ax1.set_xlabel('Time (ms)')
        self.ax1.set_ylabel('Frequency (Hz)')
        
        self.ax2.set_xlabel('Time (ms)')
        self.ax2.set_ylabel('Droplet size (pL)') 

        self.ax3.set_xlabel('Time (ms)')
        self.ax3.set_ylabel('Interdroplet spacing (ms)') 
        self.ax4.set_xlabel('Time (ms)')
        self.ax4.set_ylabel('Function performance') 

        self.ax5.set_xlabel('Time (ms)')
        self.ax5.set_ylabel('Filtered function performance') 
        
        
        for i in np.arange(len(self.picBatches)):
            selection = dropData[dropData['index']==str(i)]
            self.ax1.plot('dropStart_ms','dropFreq_Hz',data = selection)
            self.ax2.plot('dropStart_ms','dropVol_pL',data = selection)
            self.ax3.plot('dropStart_ms','dropSpace_ms',data = selection)

        
        #self.ax1.plot(data['dropStart_ms'],data['dropFreq_Hz'],c = data['index'])

        self.ax4.plot(performance['time_ms'],performance['dropPass'])
        self.ax5.plot(performance['time_ms'],performance['dropProc'])
        
        self.figCanvas1.draw()
        self.figCanvas2.draw()
        self.figCanvas3.draw()
        self.figCanvas4.draw()        
        self.figCanvas5.draw()        



    def refreshGUI(self):
        self.initGUI()
        
        
root = tk.Tk()
root.option_add('*tearOff', tk.FALSE)
root.resizable(1, 1)
GUI = directorySelection(root)
root.mainloop()

