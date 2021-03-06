#!/usr/bin/python2.7
import sys
import os
#import threading
import time
#import Queue
from multiprocessing import Process, Lock, Queue, cpu_count
import struct
import numpy
import struct
import gdal
import osr
import gdalnumeric
from gdalconst import *

exitFlag = 0
queueLock = None
writeLock = None
workQueue = None
tasks = None

class Tasks(object):
	def __init__(self):
		self.tasks = []
	
	def add(self,task):
		self.tasks.append(task)
	
	def get(self,task):
		return self.tasks[task]

class RenderSubprocess(object):
    def __init__(self, processID, processName, queue, tasks):
        self.processID = processID
        self.processName = processName
        self.queue = queue
        self.tasks = tasks
        #Variable#
        self.strip = None
        self.task = None
        self.tries = 3
        
    def run(self):
    	while not exitFlag:
    		if self.strip is None:
    			queueLock.acquire()
        		if not workQueue.empty():
            			b, inBand, outBand, y0, y, r, t = self.task = self.tasks.get(self.queue.get())
            			queueLock.release()
            			#==#
            			if t==1:
			            	#print self.processName+" reading rows "+str(y*r)+" to "+str((y*r)+r-1)+" in band "+str(b)+"."
            				try:
            					self.strip = inBand.ReadAsArray(0,y*r,inBand.XSize,r,inBand.XSize,r)
            					self.tries = 10
            				except:
            					self.strip = None
            					print "read failed.  will try again later."
            					print "y:"+str(y)
            					print "r:"+str(r)
            				
            			elif t==2:
			            	#print self.processName+" reading row "+str((y0*r)+y)+" in band "+str(b)+"."
            				try:
            					self.strip = inBand.ReadAsArray(0,(y0*r)+y,inBand.XSize,1,inBand.XSize,1)
            					self.tries = 10
            				except:
            					self.strip = None
            					print "read failed.  will try again later."
            					print "y0:"+str(y0)
            					print "y:"+str(y)
            					print "r:"+str(r)
            					print "(y0*r)+y:"+str((y0*r)+y)
            				
        		else:
            			queueLock.release()
        	else:
        		if self.tries > 0:
        			writeLock.acquire()
        			b, inBand, outBand, y0, y, r, t = self.task
        			if t==1:
			            	#print self.processName+" writing rows "+str(y*r)+" to "+str((y*r)+r-1)+" in band "+str(b)+"."
            				try:
	            				outBand.WriteArray(self.strip,0,y*r)
            					self.strip = None
            				except:
	            				self.tries = self.tries - 1
            					print "write failed.  "+str(self.tries)+" more tries."
            			elif t==2:
			            	#print self.processName+" writing row "+str((y0*r)+y)+" in band "+str(b)+"."
            				try:
            					outBand.WriteArray(self.strip,0,(y0*r)+y)
            					self.strip = None
            				except:
            					self.tries = self.tries -1
            					print "write failed.  "+str(self.tries)+" more tries."
            			writeLock.release()
            		else:
            			print "abandoning write"
            			self.strip = None
        	time.sleep(1)

def execute(subprocess):
	subprocess.run()

def main():
	if(len(sys.argv)==8):
		inputFile = sys.argv[1]
		inputBands = int(sys.argv[2])
		alphaFile = sys.argv[3]
		alphaIndex = int(sys.argv[4])
		outputFile = sys.argv[5]
		rows = int(sys.argv[6])
		numberOfThreads = int(sys.argv[7])
		if numberOfThreads > 0:
			if(os.path.exists(inputFile) and os.path.exists(alphaFile)):
				if(not os.path.exists(outputFile)):
					inputDataset = gdal.Open(inputFile,GA_ReadOnly)
					alphaDataset = gdal.Open(alphaFile,GA_ReadOnly)
					if ((not inputDataset is None) and (not alphaDataset is None)):
						outputFormat = "GTiff"
						numberOfBands = inputBands+1
						w = inputDataset.RasterXSize
						h = inputDataset.RasterYSize
						r = rows
						outputDataset = initDataset(outputFile,outputFormat,w,h,numberOfBands)
						outputDataset.SetGeoTransform(list(inputDataset.GetGeoTransform()))
						outputDataset.SetProjection(inputDataset.GetProjection())
					
						if numberOfThreads == 1:
							for b in range(inputBands):
								inBand = inputDataset.GetRasterBand(b+1)
								outBand = outputDataset.GetRasterBand(b+1)
						
								for y in range(int(inBand.YSize/r)):
									outBand.WriteArray(inBand.ReadAsArray(0,y*r,inBand.XSize,r,inBand.XSize,r),0,y*r)

								y0 = inBand.YSize/r
								for y in range(inBand.YSize%r):
									outBand.WriteArray(inBand.ReadAsArray(0,y0+y,inBand.XSize,1,inBand.XSize,1),0,y0+y)
								
							burn(alphaDataset.GetRasterBand(alphaIndex),outputDataset.GetRasterBand(numberOfBands),r)
					
						elif numberOfThreads > 1:
							global exitFlag
							global queueLock
							global writeLock
							global workQueue
							global tasks
							#
							exitFlag = 0
							queueLock = Lock()
							writeLock = Lock()
							workQueue = Queue(0)
							tasks = Tasks()
							#
							for b in range(inputBands):
								print "Adding tasks for band"+str(b)
								inBand = inputDataset.GetRasterBand(b+1)
								outBand = outputDataset.GetRasterBand(b+1)
								y0 = int(inBand.YSize/r)
								for y in range(int(inBand.YSize/r)):
									task = b+1, inBand, outBand, y0, y, r, 1
									tasks.add(task)
								for y in range(inBand.YSize%r):
									task = b+1, inBand, outBand, y0, y, r, 2
									tasks.add(task)
							print "Adding tasks for alpha band"
							inBand = alphaDataset.GetRasterBand(alphaIndex)
							outBand = outputDataset.GetRasterBand(numberOfBands)
							y0 = int(inBand.YSize/r)
							for y in range(int(inBand.YSize/r)):
								task = numberOfBands, inBand, outBand, y0, y, r, 1
								tasks.add(task)
							for y in range(inBand.YSize%r):
								task = numberOfBands, inBand, outBand, y0, y, r, 2
								tasks.add(task)
						
							print "tasks in main queue: "+str(len(tasks.tasks))
							#Add tasks to queue
							queueLock.acquire()
							for taskID in range(len(tasks.tasks)):
								workQueue.put(taskID)
							queueLock.release()
							
							processes = initProcesses(numberOfThreads)

							print "Queue is full with "+str(workQueue.qsize())+" tasks."
							print "Rendering threads will now execute."
							while not workQueue.empty():
								pass
							
							exitFlag = 1 #tell's threads it's time to quit
							
							for process in processes:
								process.join()
								
						inputDataset = None
						outputDataset = None
					else:
						print "Error Opening File"
				else:
					print "Output file already exists"
			else:
				print "Input file does not exist."
		else:
			print "You need at least 1 thread."
	else:
		print "Usage: cybergis-script-burn-alpha.py <input_file> <input_bands> <alpha_file> <alpha_band_index> <output_file> <rows> <threads>"

def burn(inBand,outBand,rows):
	r = rows
	for y in range(int(inBand.YSize/r)):
		outBand.WriteArray(inBand.ReadAsArray(0,y*r,inBand.XSize,r,inBand.XSize,r),0,y*r)

	y0 = inBand.YSize/r
	for y in range(inBand.YSize%r):
		outBand.WriteArray(inBand.ReadAsArray(0,y0+y,inBand.XSize,1,inBand.XSize,1),0,y0+y)
        
def initDataset(outputFile,f,w,h,b):
    driver = gdal.GetDriverByName(f)
    metadata = driver.GetMetadata()
    return driver.Create(outputFile,w,h,b,gdal.GDT_Byte,['ALPHA=YES'])
    
def initProcesses(count)
    print str(cpu_count())+" CPUs are available."
    processes = []
    processID = 1
    for processID in range(count):
        subprocess = RenderSubprocess(processID, ("Thread "+str(processID)), workQueue, tasks)
        process = Process(target=execute,args=(subprocess,))
        process.start()
        processes.append(process)
        processID += 1
    print "Initialized "+str(count)+" threads."
    return processes

main()    
