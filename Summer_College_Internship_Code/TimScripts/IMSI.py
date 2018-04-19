import sys
import numpy

def getopts(args):
    opts = {}
    while args:
        if args[0][0] == '-':
            opts[args[0]] = args[1]
        args = args[1:]
    return opts

#Variables
fileName = "DlMacStats.txt"
args = getopts(sys.argv)
n = 2
total = 0
if ("-n" in args):
    n = int(args["-n"])
if ("-f" in args):
    fileName = args["-f"]
file = open(fileName, 'r')
half = int(n/2)
numbers = []
Occurences = []
groups = [[],[]]
temp = n

#Gets nodes into a list
while temp > 0:
    numbers.append((n+1)- temp)
    temp-= 1

#Sets index 0 to 0
Occurences.append(0)

#Sets all occurences to 0
for i in numbers:
    Occurences.append(0)

#Gets the number of occurences for each node
num = 0
for line in file.readlines():
    num = line.split()[2]
    if (num.isalpha()):
        continue
    Occurences[int(num)] += 1
    total += 1

percentage = 0

#Gets the percentage of each node and adds to group
for i in numbers:
    percentage = (float(Occurences[i]) / float(total)) * 100
    if (i <= half):
        groups[0].append(percentage)
    else:
        groups[1].append(percentage)

print("-----------------------------------------------")

#Outputs data
i = 0
for group in groups:
    print("Group " + str(i + 1))
    print("-----------------------------------------------\nIMSI\tCount\tPercentage Of Occurence\n-----------------------------------------------")
    for u in group:
        num = numbers[group.index(u)]
        if (i != 0):
            num = num + half
        if (i == 0):
            print(str(num) + "\t" + str(Occurences[group.index(u) + 1]) + "\t" + str(round(u, 3)) + "%")
        else:
            print(str(num) + "\t" + str(Occurences[group.index(u) + 1 + half]) + "\t" + str(round(u, 3)) + "%")
    i += 1
    print("-----------------------------------------------")

#Displays the medians of group 1 and 2
groups[0].sort()
groups[1].sort()
print("Total Values Counted: " + str(total))
print("Median of 1 - " + str(half) + ": " + str(round(numpy.median(groups[0]),3)) + "%")
print("Median of " + str(half + 1) + " - " + str(n) + ": " + str(round(numpy.median(groups[1]),3)) + "%")
