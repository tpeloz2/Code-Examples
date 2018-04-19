"""
Program gets available cores from computer.
"""
import multiprocessing
import os
import sys
import subprocess
import time

def getopts(args):
    opts = {}
    while args:
        if args[0][0] == '-':
            opts[args[0]] = args[1]
        args = args[1:]
    return opts

CPUS = []
available_cpus = []
hostCore = []
host = "10.31.48.167" #Either hardcoded or not, but will contain all of the hosts
user = "tpeloz2@"
args = getopts(sys.argv)
assignments = 4
if ("-a" in args):
    assignments = int(args["-a"])
if ("-h" in args):
    host = args["-h"]
if ("-u" in args):
    user = args["-u"] + "@"
i = 0

#Accesses proc stat until no assignments available
if (assignments > 0):
    available_cpus = []
    CPUS = []
    subprocess.Popen("ssh " + user + str(host) + " cat /proc/stat > info.txt", shell=True).wait()
    cores = 0
    for line in open("info.txt", 'r'):
        if "cpu" in line:
            cores += 1
    prev_Total = [0] * cores
    prev_Idle = [0] * cores

    #print(str(cores) + " cores found.")
    i = 0

    while (i < 2):
        subprocess.Popen("ssh " + user + str(host) + " cat /proc/stat > info.txt", shell=True).wait() # Subject to change. Gonna do a loop around.
        j = 0
	
	#Grabs the core data and uses a formula to calculate current usage
        for line in open("info.txt", 'r'):
            cpu = []
            if (("cpu" in line) and (line[line.index("cpu") + 3: line.index(" ")].isdigit())):

                for word in line.split():
                    if (word.isdigit()):
                        cpu.append(float(word))

                Idle = cpu[3] + cpu[4]
                NonIdle = cpu[0] + cpu[1] + cpu[2] + cpu[5] + cpu[6] + cpu[7]
                Total = Idle + NonIdle

                # differentiate: actual value minus the previous one
                totald = Total - prev_Total[j]
                idled = Idle - prev_Idle[j]

                CPU_Percentage = (totald - idled) / totald
                prev_Total[j] = Total
                prev_Idle[j] = Idle
                j += 1

                if (i > 0):
                    CPUS.append(CPU_Percentage * 100)

        time.sleep(1)
        i += 1
	
    #Writes available cores to file
    i = 0
    for cpu in CPUS:
        with open("cpus.txt", 'a') as file:
            file.writelines(str(CPUS))
        if (cpu < 20):
            available_cpus.append(i) # Will be used in taskset later
        i += 1

    #print(str(available_cpus.__len__()) + " cores available.")
    if available_cpus.__len__() > 0:
        file = open("comm.txt", 'w')
        for cpu in available_cpus:
            file.writelines("Host:" + str(host) + " " + "Core:" + str(cpu) + "\n")
