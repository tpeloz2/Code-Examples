import multiprocessing
import os
import sys
import subprocess
import time
import fileinput

def addTask(task):
    task = subprocess.Popen(task, shell=True, bufsize=0)
    return task

hosts = []
users = []
paths = []
for line in open("hosts.txt", 'r'):
    users.append(line.split()[0])
    hosts.append(line.split()[1])
    count  = 0
    for word in line.split():
        count += 1

    #Checks for the third entry. Third entry is the path. If it does not exist then the program adds it to hosts.txt
    if (count < 3):
        subprocess.Popen("ssh "+line.split()[0]+ "@" + line.split()[1] +" find ~/ -name ns3 >> temp.txt", shell=True)
        found = 0
        for lines in open("temp.txt", 'r'):
            if ("repos2" in lines):
                for word in lines.split():
                    if (word.endswith("repos2/ns3")):
                        paths.append(word + "/")
                        found = 1
                        break

            if (found > 0):
                break

        subprocess.Popen("cat /dev/null > temp.txt", shell=True).wait()
    else:
        paths.append(line.split()[2])

#Clears nohup.out
subprocess.Popen("cat /dev/null > nohup.out", shell=True)

assignments = ['./waf --run "mqq-incast-jitter --load=0.001 --incastdegree=20 --filename=MQQ.txt --runtime=0.25"',
               './waf --run "mqq-incast-jitter --load=0.002 --incastdegree=20 --filename=MQQ1.txt --runtime=0.25"',
               './waf --run "mqq-incast-jitter --load=0.004 --incastdegree=20 --filename=MQQ2.txt --runtime=0.25"',
               './waf --run "mqq-incast-jitter --load=0.005 --incastdegree=20 --filename=MQQ3.txt --runtime=0.25"',
               './waf --run "mqq-incast-jitter --load=0.006 --incastdegree=20 --filename=MQQ4.txt --runtime=0.25"',
               './waf --run "mqq-incast-jitter --load=0.007 --incastdegree=20 --filename=MQQ5.txt --runtime=0.25"',
               './waf --run "mqq-incast-jitter --load=0.008 --incastdegree=20 --filename=MQQ6.txt --runtime=0.25"',
               './waf --run "mqq-incast-jitter --load=0.009 --incastdegree=20 --filename=MQQ7.txt --runtime=0.25"']


postAssignments = []
#Gets the CPU usage on the selected host.
cpu_get = subprocess.Popen("python cpu.py -a " + str(assignments.__len__()) + " -h " + str(hosts[0]) + " -u " + str(users[0]) + "| tee comm.txt >> nohup.out 2>&1", shell=True)

tasks = []
post_Tasks = []
files = []
errors = []
copy = []
postFiles = []
terminated = []
hostCore = [] #HostnameCore
PIDS = []
location = [] #0: Hostname/IP 1:Path To File

logfile = open("nohup.log", 'a')
count = 0
postCount = 0
h = 1

#Error checking
while (count > 0) or (assignments.__len__() > 0) or (postCount > 0):

    i = 0
    # Command line errors
    for line in open("nohup.out", 'r'):
        if ("SIG" in line) and (i not in errors):
            terminated.append(line[line.index("--filename"):line.index(".txt")])
            errors.append(i)
            print('\033[91m' + line + '\033[0m')
        i += 1

# ASSIGNMENT PORTION
    started = 0
    
    #Resets back to the first host
    if (h >= hosts.__len__()):
        h = 0
    
    #Checks if there are any tasks to assign
    if ((cpu_get.poll() != None) and ((assignments.__len__() > 0) or (postAssignments.__len__() > 0))):
        #Checks the communication file for cores if any
	for line in open("comm.txt", 'r'):
            if (os.stat("comm.txt").st_size != 0):
                host = line[line.index("t:") + 2: line.index(" ")]
                core = line[line.index("e:") + 2:line.index("\n")]
                user = users[hosts.index(host)] + "@"
                path = paths[hosts.index(host)]
		
		#Secondary check to prevent short circuiting
                if (assignments.__len__() > 0):
			
   		    #Assigns task onto core. Stores locations in parallel arrays and normal arrays. Hostcore Represents cores that are being used by this program.
                    if ((str(host + core)) not in hostCore):
                        assignments[0] = "nohup ssh -t " + user + str(host) + " \'cd "+path+"; taskset -c " + str(core) + ' ' + str(assignments[0] + "\' >>nohup.out 2>&1")
                        task = addTask(assignments[0])

                        tasks.append(task)
                        if ("--filename" in assignments[0]):
                            file = assignments[0][assignments[0].index("--filename") + 11:assignments[0].index('.txt') + 4]
                        else:
                            file = "Null"

                        files.append(file)
                        #postFiles.append(file)
                        PIDS.append(task.pid)
                        hostCore.append(str(host + core))

                        postFiles.append(file)
                        location.append([host, path, user]) #Pretty much everything in hosts.txt ex: ip_address path user
                        assignments.remove(assignments[0])
                        started += 1
                        count += 1
		
		#Post assignment to cores
                if (postAssignments.__len__() > 0):
                    if ((str(host + core)) not in hostCore):

                        #Previous pid
                        pid = int(postAssignments[0][postAssignments[0].index("(")+ 1:postAssignments[0].index(")")])
			
			#Gets the assignments
                        postAssignments[0] = postAssignments[0][postAssignments[0].index(")") +1:]
                        postAssignments[0] = "nohup ssh -X -t " + user + str(host) + " \'cd "+path+"; taskset -c " + str(core) + ' ' + str(postAssignments[0] + "\' >>nohup.out 2>&1")

			#assigns task to core
                        fileT = subprocess.Popen("nohup scp -r " + user + location[(PIDS.index(pid))][0] + ":" +location[(PIDS.index(pid))][1] + files[PIDS.index(pid)] + " " + location[(PIDS.index(pid))][2] + host + ":" + location[(PIDS.index(pid))][1] + " >> nohup.out 2>&1", shell=True)
                        fileT.wait()
                        task = addTask(postAssignments[0])

                        files.append(files[PIDS.index(pid)])
			
			#Two types of post processes checks for either one
                        if ("Graphs.py" in postAssignments[0]):
                            postFiles.append(files[PIDS.index(pid)].rstrip(".txt") + ".pdf")
                        elif ("calc_fct.py" in postAssignments[0]):
                            postFiles.append("result" + files[PIDS.index(pid)])

                        post_Tasks.append(task)
                        PIDS.append(task.pid)
                        hostCore.append(str(host + core))
                        location.append([host, path, user]) #Pretty much everything in hosts.txt
                        postAssignments.remove(postAssignments[0])
                        started += 1

        if (assignments.__len__() > 0 and (cpu_get.poll() != None)):
            cpu_get = subprocess.Popen("python cpu.py -a " + str(assignments.__len__()) + " -h " + str(hosts[h]) + "| tee comm.txt >> nohup.out 2>&1",shell=True)
            h += 1

    if (started > 0):
        print("\033[94mStarted "+ str(started) + " tasks.\033[0m")

# TASK PORTION
    for task in tasks:

        #Removes and reports errors
        if (task.poll() != None) and (task.poll() != 0):
            print("Process " + str(task.pid) + " failed with file " + str(files[PIDS.index(task.pid)]) + " and return code: " + str(task.returncode))
            hostCore[PIDS.index(task.pid)] = "-1"
            tasks.remove(task)
            count -= 1
	
	#Checks for task completion
        elif (task.poll() != None) and (task.poll() == 0):
            print(str(task.pid) + ": Task Complete")
            file = files[PIDS.index(task.pid)] #Gets the index of the parallel array

            postAssignments.append("(" + str(task.pid)+")python " + "Graphs.py -f " + file)
            postAssignments.append("(" + str(task.pid) + ")python " + "calc_fct.py -i " + file)

            hostCore[PIDS.index(task.pid)] = "-1"
            
	    #Copies output files to this computer
	    subprocess.Popen("nohup scp -r " + location[(PIDS.index(task.pid))][2] + location[(PIDS.index(task.pid))][0] + ":" + location[(PIDS.index(task.pid))][1] + "/" + files[PIDS.index(task.pid)] + " . >> nohup.out 2>&1", shell=True)
            tasks.remove(task)
            count -= 1
            postCount += 2

    #Checks if there are post process tasks assigned
    for pos in post_Tasks:
        if (pos.poll() != None) and (pos.poll() != 0):
            print("Post Process " + str(pos.pid) + " failed " + str(files[PIDS.index(pos.pid)]) + " and return code: " + str(pos.returncode))
            hostCore[PIDS.index(pos.pid)] = "-1"
            post_Tasks.remove(pos)
            postCount -= 1

        elif (pos.poll() != None) and (pos.poll() == 0):
            print(str(pos.pid) + ": Post Process Task Complete")
            hostCore[PIDS.index(pos.pid)] = "-1"
            cop = subprocess.Popen("nohup scp -r " + location[(PIDS.index(pos.pid))][2] + location[(PIDS.index(pos.pid))][0] + ":" +location[(PIDS.index(pos.pid))][1] + "/" + postFiles[PIDS.index(pos.pid)] + " . >> nohup.out 2>&1", shell=True)
            copy.append(cop)
            cop.wait()
            subprocess.Popen("nohup ssh " + location[(PIDS.index(pos.pid))][2] + location[(PIDS.index(pos.pid))][0] + " rm -r " + location[(PIDS.index(pos.pid))][1] + "/" + postFiles[PIDS.index(pos.pid)] + " >> nohup.out 2>&1", shell=True)
            post_Tasks.remove(pos)
            postCount -= 1

#Post Process Checks
for c in copy:
    if (c.poll() == None):
        c.wait()

#Checks if files were made
for i in postFiles:
    if i in os.listdir(os.curdir):
        continue
    else:
        print("File " + i + " failed to be created.")

#Deletes everything involving(created by) this program in the host computers
postFiles = []
i = 0
for host in hosts:
    path = paths[hosts.index(host)]
    subprocess.Popen("nohup ssh -t " + users[i] + "@" + host + " \'cd " + path + "; dir\' >> info.txt 2>&1", shell=True).wait()
    for line in open("info.txt", 'r'):
        for file in files:
            if (file in line) and (file not in postFiles):
                subprocess.Popen("nohup ssh " + users[i] + "@" + host + " rm -r " + path + file +" >> nohup.out 2>&1", shell=True)
                postFiles.append(file)
    i += 1

#Adds Nohup.out to Nohup.log
for line in open("nohup.out", 'r'):
    logfile.write(line)

logfile.write("---------------------------------------------------------------------------------------------------------------------------\n")

print("\033[32mAll Tasks Finished \033[0m")
