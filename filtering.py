# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 15:53:35 2017

@author: anonymous
"""
import numpy as np
import time


def init_filt_var():
    '''variables for new filter'''
    global rawWinSize
    global counter
    global rawDataVectorAll, meanDataVectorAll
    rawWinSize = 5

    counter = 0
    rawDataVectorAll = [[] for i in range(8)]
    meanDataVectorAll = [0 for i in range(8)]


def data_filtering(data):
    global rawWinSize
    global counter
    global rawDataVectorAll, meanDataVectorAll

    counter += 1

    # print('data',data)
    # print('counter',counter)

    # condition at the beginning of recording
    if counter <= rawWinSize:
        for i in range(len(data)):
            rawDataVectorAll[i].append(data[i])
            mean = np.mean(rawDataVectorAll[i][0:counter])
            meanDataVectorAll[i] = mean

        return meanDataVectorAll
    else:
        for i in range(len(data)):
            rawDataVectorAll[i].append(data[i])
            mean = np.mean(rawDataVectorAll[i][counter-rawWinSize:counter])
            meanDataVectorAll[i] = mean

        return meanDataVectorAll


def save_output_to_file():
    global timeVector, outputDataVector
    fileName = "OutputData"
    print (fileName)
    f = open(fileName+".txt", "w+")

    for i in range(0, len(timeVector)):
        f.write(str(timeVector[i]))
        for j in range(len(outputDataVector)):
            f.write("\t")
            f.write(str(outputDataVector[i][j]))
        f.write("\n")
    f.close()
