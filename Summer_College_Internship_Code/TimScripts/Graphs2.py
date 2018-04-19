import matplotlib.pyplot as plt
import sys #args: filePath, amount of Nodes
from matplotlib.backends.backend_pdf import PdfPages

#FindNth
#Finds the nth char in a string sequence
#Parameters: string, character you are looking for, and nth one
#Returns the index of the nth char
def findNth(line, char, n):
    index = 0
    for chars in line:
        if chars == char:
            n -= 1
        if n == 0:
            return index
        index += 1
    return -1

def getopts(args):
    opts = {}
    while args:
        if args[0][0] == '-':
            opts[args[0]] = args [1]
        args = args[1:]
    return opts


#Variable names and initializations/ Get options
args = getopts(sys.argv)
fileName = "RXlteReno4UE.txt"
nodes = 1

#determines what type of data it is
if "-f" in args:
    fileName = args["-f"]
if "-n" in args:
    nodes = int(args["-n"])

#Opens file
file = open(fileName, "r") #Sets the text to the fileName

#Axes
times = [[] for x in range(nodes)]
throughputs = [[] for x in range(nodes)]

#Goes through each line and gets the data
for line in file:
    line.rstrip("\n") #Removes \n escape sequence from the string
    secondColon = findNth(line, ':', 2) #Gets the index of the second colon
    thirdColon = findNth(line, ':', 3)  #^ except with third colon
    node = float(line[5:secondColon])  #Finds the node number in the line

    # Sorts the lines into their respective nodes. Think of bins
    i = 0
    while i < nodes:
        if i == node:
            times[i].append(float(line[secondColon + 1:thirdColon]))
            throughputs[i].append(float(line[thirdColon + 1:]))
        i+=1

#Plots 4 lines with their respective names
i = 0
while (i < nodes):
    plt.plot(times[i],throughputs[i], label = ("Node " + str(i)))
    i+=1

#Allows the resizing of the screen
manager = plt.get_current_fig_manager()
manager.resize(*manager.window.maxsize())

#Adds a legend, labels, and title
fileName = fileName.rstrip(".txt")
plt.legend(bbox_to_anchor=(.8, 1.00), loc=2, borderaxespad=0.)
plt.title(fileName + ": Throughput vs. Time")
plt.xlabel("Time(microseconds)")
plt.ylabel("Throughput")
plt.savefig(fileName, format = 'pdf')

plt.show()