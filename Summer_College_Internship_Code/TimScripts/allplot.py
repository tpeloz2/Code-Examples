#!/usr/bin/python

import sys
import getopt
import numpy as np
import matplotlib.pyplot as plt
import math

statsFile="utily.txt"
numOfUE = 0.0
list_of_throughput = [[]]
list_of_time = []
list_of_plotlabels = []

def ReadArgs(argv):
	global statsFile
	global numOfUE
	statsfile = ''
	numofUe = ''
   	try:
		opts, args = getopt.getopt(argv,"hi:n:",["ifile=","ofile="])
	except getopt.GetoptError:
		print 'usage: python my_plotter.py -i <inputfile> -n <numberofue>'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'usage: python my_plotter.py -i <inputfile>'
			sys.exit()
		elif opt in ("-i", "--ifile"):
			statsfile = arg
			statsFile = statsfile
      		elif opt in ("-n", "--ofile"):
         		numofUe = arg
			numOfUE = int(numofUe)
	print 'Stats file is ', statsFile
	print 'Number of Ue are', numOfUE

def ReadFile():
        global list_of_throughput
	global list_of_UE
	global list_of_time
	global list_of_plotlabels
	for i in range(0,numOfUE + 1): #In case of more than 21 UE
		list_of_plotlabels.append(str(i) + "UE")

	time,UE,throughput = np.loadtxt(statsFile, delimiter=':' , usecols = (0,2,4), dtype =  str , unpack=True)
	offset = int(time[0]) - 1	
	print time
	print UE
	print throughput
	print len(time)
	dummy = (len(time))/numOfUE
	print(str(dummy))
	list_of_throughput = [[0 for i in xrange(dummy+1)] for i in xrange(numOfUE+1)]
	list_of_time.append(0)
        for i in range (0,len(time),numOfUE):
                list_of_time.append(time[i])
	for i in range(0,len(time)):
		list_of_throughput[int(UE[i])][int(time[i]) - offset] = float(throughput[i]) # Some files wont start at 1 second, so an offset is needed to compensate
	for i in range (0,len(list_of_time)):
		list_of_time[i] = float(list_of_time[i])
	print list_of_throughput
	print list_of_time

def AverageValues():	
	global list_of_throughput
	global list_of_time
	global numOfUE
	
	file = open(statsFile.rstrip('.txt') + 'Avg.txt','w')
	listOfValues = []
	total = 0.0
	average = 0.0
	n = 0	
	listOfValues.append([])
	
	#Gets the average and the total
	for i in range(1, numOfUE + 1):
		listOfValues.append([])
		for num in list_of_throughput[i]:
			total += num
		
		total = total - (list_of_throughput[i][0] + list_of_throughput[i][1])
		average = total/(len(list_of_time)-2)
		listOfValues[i].append(total)
		listOfValues[i].append(average)
		total = 0.0
		average = 0.0
	
	#Prints the averages
	for i in range(1, numOfUE + 1):
		print("User " + str(i) + " : " + str(listOfValues[i][1]) + "\tTotal: " + str(listOfValues[i][0])) 
		file.write(str(i) + ":Average:" + str(listOfValues[i][1]) + ":Total:" + str(listOfValues[i][0]) + "\n")
	
	
	
def PlotThroughput():
	global list_of_throughput
	print numOfUE
	fig, ax = plt.subplots( nrows=1, ncols=1 )
	fileName = statsFile.rstrip(".txt")
	for i in range(1,numOfUE+1):
		ax.plot(list_of_time,list_of_throughput[i] , label = list_of_plotlabels[i] )
	ax.set_ylabel('Throughput (Mbps)')
	ax.set_xlabel('Time in Seconds (s)')
	# Now add the legend with some customizations.
	legend = ax.legend(loc='upper right', shadow=True)

	# The frame is matplotlib.patches.Rectangle instance surrounding the legend.
	frame = legend.get_frame()
	frame.set_facecolor('0.90')

	# Set the fontsize
	for label in legend.get_texts():
    		label.set_fontsize('large')

	for label in legend.get_lines():
    		label.set_linewidth(1.5)  # the legend line width
	fig.savefig(fileName + ".pdf", format = 'pdf')

if __name__=="__main__":
	ReadArgs(sys.argv[1:])
	ReadFile()
	PlotThroughput()
	AverageValues()
