# -*- coding: utf-8 -*-
"""
Created on Mon Oct 06 15:33:54 2014

@author: lleonard
"""
import csv
import os
import numpy as np
from operator import itemgetter

#Initialize variables
EQE_data = [[],[]]
Sample = np.zeros((195,4))

#Define file location
"""
Make sure folder is saved in C:/Users/eso/Documents/Spectrophotometer Results/
"""
folder = input("Please enter name of folder: ")
top = "C:/Users/eso/Documents/Spectrophotometer Results/" + folder

"""
Define Summary Directory location.  If the summary directory isn't there,
create a folder in the specified location
"""
SummaryDir = top + '/Summary'
if not os.path.exists(SummaryDir):
    os.makedirs(SummaryDir)

#Create the summary file and define the column names
SummaryFile = SummaryDir + "/Summary" + folder +".csv"
sf = open(SummaryFile, 'w')
eqe = open("C:/Users/eso/Documents/Spectrophotometer Results/IQE.csv", 'r')

#Read EQE File and move data into lists
eqefile = csv.reader(eqe)
for lines in eqefile:
    EQE_data[1].append(float(lines[1]))
    EQE_data[0].append(float(lines[0]))
eqe.close()

#Process Data
for filename in os.listdir(top):
    
    if filename == 'Results Table.csv' or filename == 'Sample Table.csv' or filename == 'Results Table (2).csv' or filename == 'Sample Table (2).csv':
        break
    
    if filename.endswith('csv'):
        
        f = open(top + '\\' + filename, 'r') 
        datafile = csv.reader(f)
        count = 0
        
        for lines1 in datafile:
            
            if lines1[1] != ' %R':
                Sample[count, 1] = float(lines1[1])
            
            if lines1[0] != 'nm':
                Sample[count, 0] = float(lines1[0])
                count = count + 1
   
        SampleSorted = sorted(Sample, key=itemgetter(0), reverse = False)
        sum1 = 0
        sum2 = 0

        for nm in range(len(SampleSorted)):
            if SampleSorted[nm][0] > EQE_data[0][0] and SampleSorted[nm][0] < EQE_data[0][-1]:
                SampleSorted[nm][2] = np.interp(SampleSorted[nm][0], EQE_data[0], EQE_data[1])
                sum2 = sum2 + SampleSorted[nm][2]
                
        for i in range(len(SampleSorted)):
            SampleSorted[i][3] = SampleSorted[i][1] * SampleSorted[i][2]
            sum1 = sum1 + SampleSorted[i][3]
            
        f.close()
        avg = sum1/sum2
        sf.write(str(filename) + ', ' + str(avg) + '\n')
  
sf.close()