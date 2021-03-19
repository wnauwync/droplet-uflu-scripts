# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 15:46:21 2021

@author: wnauwync
"""

##############################################################################
#
#                              DROPLET ANALYSIS                              #
#
##############################################################################

#-----------------------------------------------------------------------------
#IMPORT LIBRARIES
#-----------------------------------------------------------------------------

import skimage
from skimage import io
from skimage import filters
from scipy import ndimage
from natsort import natsorted, ns
from itertools import accumulate, groupby
from datetime import datetime
import glob
import math
import csv
import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from array2gif import write_gif

#-----------------------------------------------------------------------------

#INPUT: directory with name YYYYMMDD_fps (files are ordered from start time to
# end time), amount of images to consider, 
#flow rate in uL/hr

#OUTPUT: Text file (dateTIME_freq) with frequency, droplet size, time of 
#results display

#Image capture guidelines: edge should be free of debris, channel geometry
#should be visible for image processing to work
#make sure channel geometry is parallel to camera frame
#Make sure first image has a droplet shown on it because it is used to 
#determine initial parameters

#Maybe try drop detection method file:///C:/Users/wnauwync/AppData/Local/Temp/sensors-16-00218-v2.pdf
https://www.youtube.com/watch?v=sHpFGO3Jh3E&list=PLqdo5Two_cXhm-twPwbpeV4aCSFE85_in&index=2




def determineThreshold(image):
    #In ImageJ: 19.85 % of highest scoring pixels are set to True, rest is 
    #set to False
    #find lowest value, find highest value, select all values that are more 
    #than 33/116*delta(maxmin) and make them True, make rest False
    #33/116 was determined through imageJ
    #if not successful, try selecting percentage of a histogram
    
    maxVal = np.amax(image)
    minVal = np.amin(image)
    threshold = 38/116*(maxVal-minVal)
    
    return threshold

def channelDetection(image):
    #Takes a single image and calculates edges to be considered
    #border is either True or False
    #True: there is a border of FALSE/TRUE values on the picture that should
    #be ignored
    #False: there is no border, take into account border values

    rowValues = np.sum(image,axis = 1)>0.7*len(image[0])
    groups = list(accumulate(sum(1 for _ in g) for _,g in groupby(rowValues)))
    groups.remove(len(image))
    
    start = groups[0]
    end = groups[len(groups)-1]
    delta = (end-start)/3
    edgevector = np.arange(start+delta,end-delta)
    edgevector = edgevector.astype(int)
    
    return edgevector


def correctEdges(image):
    image[:,len(image[0])-1] = True
    image[len(image)-1,:] = False
    return image

    
    # for i in np.arange(len(image)):
    #     image[i,0] = image[i,1]
    #     image[i,len(image[0])-1] = image[i,len(image[0])-2]

    

def detectEdge(image,edgevector):
    #Let's say if there are more then 5 True pixels, a droplet is passing by
    detectionZone = image[edgevector,len(image[0])-2]
    
    if sum(detectionZone)>5:
        return True
    else:
        return False
    

def detectDroplet(passList): 
    
    #do not include half droplets, only look at 
    
    dropStart = []
    dropStop = []
    previousElement = False
    start = passList.index(False)
    end = passList.index(False, len(passList)-1)
    
    

    for i in np.arange(start,end+1,1):
        
        if passList[i] == True:
            if previousElement == False:
                dropStart.append(i)
        if passList[i] == False:
            if previousElement == True:
                dropStop.append(i)
        previousElement = passList[i]
    
    
    #filter out single or double frame droplets (false positives)
    toRemove = []
    for i in np.arange(len(dropStart)):
        delta = dropStop[i]-dropStart[i]        
        if delta < 3:
            dropStart[i] = False
            dropStop[i] = False

    dropStart = list(filter(None,dropStart))
    dropStop = list(filter(None,dropStop))
    
    #list with beginpoints of droplets
    #list with endpoints of droplets
        
    dropAmount = len(dropStart)
    imageAmount = (end-start)+1 
    
    
    return [dropAmount,imageAmount]




def writeToTsv(dropFreq,dropSize,flowrate,newTxt):
    #write tsv-file in directory 'dropletData'
    #add to existing file on same date
    #add to new file if different date
    #OR if specified

    #Data:
    #Date || Time || Flow rate (ul/hr) || Droplet size (pL) || Droplet frequency (Hz) 
    
    date = datetime.today().strftime('%Y%m%d')
    time = datetime.today().strftime('%H%M%S')
    fileName = date + '_' + time + '.tsv'
    
    if newTxt == False:
        #find most recent file to append to in dir
        #if none found, make new one anyway
        list_tsvfiles = []
        for file in os.listdir('dropletData/'):
            if file.endswith('.tsv'):
                list_tsvfiles.append(file)
            
            
        if list_tsvfiles:
            list_tsvfiles = natsorted(list_tsvfiles)
            fileName = list_tsvfiles[len(list_tsvfiles)-1]
            with open('dropletData/' + fileName,'a') as out_file:
                tsv_writer= csv.writer(out_file, delimiter = '\t')
                tsv_writer.writerow([date,time,flowrate,dropSize,dropFreq])
            
        if not list_tsvfiles:
            newTxt = True
    
    if newTxt == True:
        with open('dropletData/' + fileName ,'wt') as out_file:
            tsv_writer= csv.writer(out_file, delimiter = '\t')
            tsv_writer.writerow(['Date','Time','Flow rate (uL/hr)','Droplet size (pL)','Droplet frequency (Hz)'])
            tsv_writer.writerow([date,time,flowrate,dropSize,dropFreq])

        
def createDir():
    currentDir = os.listdir()
    #Check for presence of used directories
    if 'dropletData' not in currentDir:
        os.mkdir('dropletData/')
    if 'imageData' not in currentDir:
        os.mkdir('imageData/')
    

def addRGB(image_list):
    #show true as RED, false as WHITE
    image_listRGB = []
    for i in np.arange(len(image_list)):
        R = image_list[i]*255
        G = image_list[i]*0
        B = image_list[i]*0
        RGB_list = np.array([R,G,B])
        image_listRGB.append(RGB_list)
    return np.array(image_listRGB)
    
    
def plotData(fileName = False):
    #if no input, take earliest made tsv file
    #if input go to dropData/fileName
    
    if fileName == False:
        list_files = natsorted(os.listdir('dropletData/'))
        fileName = list_files[len(list_files)-1]
        fileName = fileName[0:len(fileName)-4]
        
    data = pd.read_csv('dropletData/' + fileName + '.tsv',sep='\t')
    deltaTList = [0]
    FMT = '%Y%m%d%H%M%S'
    
    startTime = str(data.iloc[0,0])+str(data.iloc[0,1])
    startTime = datetime.strptime(startTime,FMT)

    for i in np.arange(1,len(data)):
        endTime = str(data.iloc[i,0])+str(data.iloc[i,1])
        endTime = datetime.strptime(endTime,FMT)
        deltaT = endTime-startTime
        deltaTList.append(deltaT.seconds)
    
    data['deltaT (s)'] = deltaTList
    
    
    #Plot data 
    #axis 1 is frequency
    #axis 2 is droplet size
    
    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Frequency (Hz)', color=color)
    ax1.plot(data['deltaT (s)'], data['Droplet frequency (Hz)'], color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    
    color = 'tab:blue'
    ax2.set_ylabel('Droplet size (pL)', color=color)
    ax2.plot(data['deltaT (s)'], data['Droplet size (pL)'], color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.savefig('imageData/' + fileName + '_Plot' + '.png',dpi = 300,format = 'png')
    
    

def dropletCounter(directory,flowrate,newTxt,newGif=False):
    #provide flowrate in uL/hr
    #Read files in directory into numpy arrays
    currentPath = os.getcwd()
    os.chdir(currentPath)
    
    #Make necessary directories
    #Check for presence of used directories
    currentDir = os.listdir()

    if 'dropletData' not in currentDir:
        os.mkdir('dropletData/')
    if 'imageData' not in currentDir:
        os.mkdir('imageData/')
        
    
    list_files = os.listdir(directory + '/')
    list_files = natsorted(list_files)
    image_list = []
    passList = []
    for filename in list_files:
        image_list.append(io.imread(directory + '/' + filename))
    

    for i in np.arange(len(image_list)):
        #Image processing --> detect edges, make binary according to threshold
        #and fill holes
        image = image_list[i]
        image = filters.sobel(image)
        if i == 0:
            thresh = determineThreshold(image)
        image = image>thresh
        image = correctEdges(image)
        image = ndimage.binary_fill_holes(image)
        if i == 0:
            edgeVector = channelDetection(image)
            
        image_list[i] = image
        passList.append(detectEdge(image,edgeVector))
        
    [dropAmount,imageAmount] = detectDroplet(passList)
    fps = int(directory.split("_")[1])
    
    dropFreq = dropAmount/(imageAmount/fps) #in Hz
    dropSize = flowrate/3600*10**6/dropFreq #in pL
    
    date = datetime.today().strftime('%Y%m%d')
    time = datetime.today().strftime('%H%M%S')
    
    writeToTsv(dropFreq,dropSize,flowrate,newTxt)
    image_listRGB = addRGB(image_list)
    
    if newGif == True:
        write_gif(image_listRGB,'imageData/'+ str(date) + '_' + str(time)+'.gif',fps = 10)
        