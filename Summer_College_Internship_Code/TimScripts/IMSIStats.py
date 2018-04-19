import sys
import math
import numpy

def getopts(args):
    opts = {}
    while args:
        if args[0][0] == '-':
            opts[args[0]] = args[1]
        args = args[1:]
    return opts

#variables
fileName = "UlSinrStats2UEs.txt"
args = getopts(sys.argv)
n = 2
if ("-n" in args):
    n = int(args["-n"])
if ("-f" in args):
    fileName = args["-f"]
file = open(fileName, 'r')
outputFile = open(fileName.rstrip(".txt") + "OutPut.txt", 'w')
Users = []
Values = [[]]
Means = [0]
Medians = [0]
Maxs = [0]
Mins = [0]
temp = n

#Saves spots for each node in each array
while temp > 0:
    Users.append((n+1)- temp)
    Values.append([])
    Means.append(0)
    Medians.append(0)
    Maxs.append(0)
    Mins.append(0)
    temp-= 1

#Grabs data and imsi values. Converts to log base 10.
val = 0
imsi = 0
for line in file.readlines():
    val = line.split()[4]
    if (str(val).isalpha()):
        continue
    imsi = int(line.split()[2])
    if (imsi > n):
        continue
    val = float(val)
    val = 10 * math.log(val, 10)
    Values[imsi].append(val)

#Calculates mean, median, max, and min for each node.
for i in Users:
    Means[i] = numpy.mean(Values[i])
    Medians[i] = numpy.median(Values[i])
    Maxs[i] = numpy.max(Values[i])
    Mins[i] = numpy.min(Values[i])

#Header
outputFile.writelines("File: " + fileName + "\n")
outputFile.writelines("----------------------------------------------" + "\n")
print("File: " + fileName)
print("----------------------------------------------")

#Writes to both a file and on the terminal
for u in Users:
    outputFile.writelines("User\t" + str(u) + "\n")
    outputFile.writelines("Mean:\t" + str(Means[u]) + "\n")
    outputFile.writelines("Median:\t" + str(Medians[u]) + "\n")
    outputFile.writelines("Max:\t" + str(Maxs[u]) + "\n")
    outputFile.writelines("Min:\t" + str(Mins[u]) + "\n")
    outputFile.writelines("----------------------------------------------" + "\n")
    print("User " + str(u))
    print("Mean:\t" + str(Means[u]))
    print("Median:\t" + str(Medians[u]))
    print("Max:\t" + str(Maxs[u]))
    print("Min:\t" + str(Mins[u]))
    print("----------------------------------------------")
