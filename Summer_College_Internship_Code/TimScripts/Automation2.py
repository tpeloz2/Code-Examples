import subprocess
import sys
import time
import os

#Exe youd like to execute
def addTask(task):
    if (task.endswith('.py')):
        task = ['python', task]
    task = subprocess.Popen(task,shell=True)
    return task

def findNth(line, char, n):
    index = 0
    for chars in line:
        if chars == char:
            n -= 1
        if n == 0:
            return index
        index += 1
    return -1

subprocess.Popen('cat /dev/null > nohup.out', shell=True)
#seperate commands
assignments = ['nohup ./waf --run "scratch/lte-probe --filename=TCP.txt --flowsize=16*1024*1024 --numberOfueNodes=10" >>nohup.out 2>&1',
               'nohup ./waf --run "scratch/lte-probe --filename=TCP1.txt --numberOfueNodes=7 --flowsize=16*1024*1024" >>nohup.out 2>&1',
               'nohup ./waf --run "scratch/lte-probe --filename=TCP2.txt --numberOfueNodes=1 --flowsize=16*1024*1024" >>nohup.out 2>&1',
               'nohup ./waf --run "scratch/lte-probe --filename=TCP3.txt --flowsize=16*1024*1024 --numberOfueNodes=2" >>nohup.out 2>&1',
               'nohup ./waf --run "scratch/lte-probe --filename=TCP4.txt --numberOfueNodes=5 --flowsize=16*1024*1024" >>nohup.out 2>&1']

numOfUE = []
tasks = []
outputFiles = []
errors = []
postFiles = []
terminated = []
PIDS = []
list = 0
post_Process = []
logfile = open("nohup.log", 'a')


print("Starting " + str(assignments.__len__()) + " Tasks")

#assignment of tasks
for i in assignments:
    tasks.append(addTask(i))
    PIDS.append(tasks[tasks.__len__() - 1].pid)
    outputFiles.append(i[i.index("filename=")+9:i.index('.txt')+4])
    if ("numberOfueNodes=" in i):
        index = i.index("numberOfueNodes=")+16
        if (i.find(" ", index, i.index('"', index)) > 0): # Essentially if it can find a space before the last quotation mark 
            numOfUE.append(int(i[index:i.index(" ",index)]))
        else:                                             # Otherwise the endpoint is determined as the index of the quotation mark
            numOfUE.append(int(i[index:i.index('"', index)]))
    else:
        numOfUE.append(-1)

for i in outputFiles:
    i = i.rstrip(".txt")

    postFiles.append("RX" + i + ".pdf")
    postFiles.append(i + ".pdf")
    postFiles.append("Probe" + i + ".pdf")

count = tasks.__len__() #Represents the amount of main tasks to complete
postCount = 0 #Represents the amount of post process tasks to complete
#While there are any tasks jobs or post processes
while (count > 0) or (postCount > 0):

    i = 0
    #Command line errors
    for line in open("nohup.out", 'r'):
        if ("SIG" in line) and (i not in errors):
            terminated.append(line[line.index("--filename"):line.index(".txt")])
            errors.append(i)
            print('\033[91m' + line + '\033[0m')
        i += 1

    for task in tasks:

        #Removes and reports errors
        if (task.poll() != None) and (task.poll() != 0):
            print("Process " + str(task.pid) + " failed with file " + str(outputFiles[PIDS.index(task.pid)]) + " and return code: " + str(task.returncode))
            tasks.remove(task)
            count -= 1
	
	#Checks if initial processes are done and assigns 3 new subprocesses
        elif (task.poll() != None) and (task.poll() == 0):
            print(str(task.pid) + ": Task Complete")
            file = outputFiles[PIDS.index(task.pid)] #Gets the index of the parallel array

            if (numOfUE[PIDS.index(task.pid)] is -1):
                numUE = ''
            else:
                numUE = ' -n ' + (str(2*numOfUE[PIDS.index(task.pid)]))

            new_Task = subprocess.Popen('nohup python interpacket.py -i ' + 'RX' + file + ' -n 1 >>nohup.out 2>&1', shell=True)
            PIDS.append(new_Task.pid)
            outputFiles.append(file)  # Assigns a post process task
            post_Process.append(new_Task)  # Assigns a post process task
            new_Task = subprocess.Popen('nohup python rttplotter.py -i ' + 'Probe' + file + ' -n 1 >>nohup.out 2>&1', shell=True)
            PIDS.append(new_Task.pid)
            outputFiles.append(file)  # Assigns a post process task
            post_Process.append(new_Task)  # Assigns a post process task
            new_Task = subprocess.Popen('nohup python allplot.py -i ' + file + numUE + ' >>nohup.out 2>&1', shell=True)
            PIDS.append(new_Task.pid)
            outputFiles.append(file)  # Assigns a post process task
            post_Process.append(new_Task) #Assigns a post process task
            tasks.remove(task)
            count -= 1
            postCount += 3 #Flags that there is a post process running

    #Checks if there are post process tasks assigned
    if (postCount > 0):
        for pos in post_Process:
            if (pos.poll() != None) and (pos.poll() != 0):
                print("Post Process " + str(pos.pid) + " failed " + str(outputFiles[PIDS.index(pos.pid)]) + " and return code: " + str(pos.returncode))
                post_Process.remove(pos)
                postCount -= 1

            elif (pos.poll() != None) and (pos.poll() == 0):
                print(str(pos.pid) + ": Post Process Task Complete")
                post_Process.remove(pos)
                postCount -= 1

for i in postFiles:
    if i in os.listdir(os.curdir):
        continue
    else:
        print("File " + i + " failed to be created.")

for line in open("nohup.out", 'r'):
    logfile.write(line)

logfile.write("---------------------------------------------------------------------------------------------------------------------------\n")

print("All Tasks finished")
