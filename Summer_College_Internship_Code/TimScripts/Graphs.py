import matplotlib
import matplotlib.pyplot as plt
import sys



def getopts(args):
    opts = {}
    while args:
        if args[0][0] == '-':
            opts[args[0]] = args[1]
        args = args[1:]
    return opts

args = getopts(sys.argv)
fileName = "Simple.txt"

if ("-f" in args):
    fileName = args["-f"]

file = open(fileName, "r") #Sets the text to the fileName
numberOfLines = 0          #Number of lines in the text file
interval = 0               #Percentile interval
temp = 0                   #Acts as a temporary variable to add values to the y axis

#Axis
x_axis = [] #Latency Flow
y_axis = [] #Percentile

#Reads the contents of the file to a variable [27:34]
for line in file:
    start = line.find("(ms):") + 5  #Gets the index at the start of the number just after (ms):
    end = line.find("size")         #Gets the index at the end of the number just before size
    found = float(line[start: end]) #Grabs the latency flow value. Converts it to a float
    x_axis.append(found)            #Adds the latency value to the end of the list
    numberOfLines += 1

#Sorts Latencies
x_axis.sort()

i = 0

#Gets Y Axis
while i < numberOfLines:
    i += 1
    y_axis.append(float(i/float(numberOfLines)) * 100)

#Allows the resizing of the screen
manager = plt.get_current_fig_manager()
manager.full_screen_toggle()

#Plots the points on a graph
plt.plot(x_axis, y_axis)

#Title and Labels
fileName = fileName.rstrip(".txt")
plt.title(fileName + ": Percentile vs Latency")
plt.ylabel("Percentile")
plt.xlabel("Flow Latency(ms)")
plt.savefig(fileName + ".pdf", format = 'pdf')
