#!/usr/bin/python

import sys
import numpy as np
from operator import itemgetter
import pandas as pd

def file_reaccess(path,offset,lenght):
	files={}
	fd = open("file.sizes", 'r')
	fd2 = open("file.reacc", 'w')
	for line in fd:
		value = line.split(" ")
		fd2.write(value[0] + " ")
		arr = np.zeros(int(value[2]))
		for i in range(len(path)):	
			if arr[int(offset[i]):int(lenght[i])] == 0:
				arr[int(offset[i]):int(lenght[i])] = 1	
			else:
				break;
		index=np.count_nonzero(arr==1)
		fd2.write(index, "\n")
	fd2.close()
	fd.close()

def read_traces(argv):
	udict={}
	source=[]
	date=[]
	path=[]
	cache=[]
	offset=[]
	lenght=[]
	udict={}
	size=0
	total_access_bytes=0
	fd = open(sys.argv[1], 'r')
	for line in fd:
                value = line.split(" ")
		source.append(value[0])
		value[1]= value[1].replace("[","")
		value[1]= value[1].replace("]","")
		date.append(value[1])
		url = value[2].split("?")
		d_name = url[0].split("celfs/read/")[1]
                path.append(d_name)
		try:
			val = url[1].split("offset=")[1]
			lenght.append(int(val.split("length=")[1]))
        		total_access_bytes+=int(val.split("length=")[1])
                   	offset.append(int(val.split("&")[0]))
                	cache.append(value[3].replace("\n",""))
		except IndexError, e:
			 print e 
			 print "line =", line
			 lenght.append(0)
			 offset.append(0)
			 cache.append("non")
			 udict,size = f_size(url,lenght, offset, udict ,size)		
	print "Total accesses in bytes : ", total_access_bytes
	return source, date, path, lenght, offset ,cache



def uniq_files(source, date, path, lenght, offset ,cache):
	udict={}
	counter=0
	size=0
	index=0
	total_access_bytes=0
	for i in path:
		total_access_bytes += lenght[index]	
		if i not in udict:
			udict[i] = int(lenght[index])
		else:
			udict[i] =0 
		index+=1
	print "# of Unique URL/Files: ", len(udict)
	
	for i in udict:
		if(udict[i]!=0):
			counter+=1;
			size += udict[i]
	print "# of Files accessed only 1 times: " , counter , "total bytes " , size
	print "Total accesses in bytes : ", total_access_bytes

def f_size(url,lenght, offset, udict ,size):
	if url not in udict:
         	udict[url] = [offset+lenght]
                if size < udict[url]:
                	size = udict[path[url]]


        else:
        	if (offset+lenght) > udict[url] :
                	udict[url]= [offset+lenght]
                if size < udict[url]:
                        size = udict[url]
	return udict,size


def  file_size(source, date, path, lenght, offset ,cache):
	index=0;
	udict={}
	mini=0
	maxi=0
	size=0
	for i in range(len(path)):
		if path[i] not in udict:
			udict[path[i]] = offset[i]+lenght[i]			
			if size < udict[path[i]]:
				size = udict[path[i]]
		
		else:
			if (offset[i]+lenght[i]) > udict[path[i]] :
				udict[path[i]]= offset[i]+lenght[i]
			if size < udict[path[i]]:
                                size = udict[path[i]]

	print "Biggest File Size is: " ,size
	fd = open("file.sizes", 'w')
	for i in udict:
		line = i + " "  +" " +str(udict[i] ) +"\n"
		fd.write(line)		
	fd.close()

def occur(source, date, path, lenght, offset ,cache):
	udict={}
	counter =0
	access=0
	for i in range(len(path)):
		if path[i] not in udict:
			udict[path[i]]= [offset[i],offset[i]+lenght[i]]
		else:
			if (udict[path[i]][0] <= offset[i]) and (offset[i]+lenght[i] <= udict[path[i]][1]):
				access += lenght[i]

			elif ( offset[i] <= udict[path[i]][0] ) and  (offset[i]+lenght[i] <= udict[path[i]][1]) :
				access+=offset[i]+lenght[i]-udict[path[i]][0]				
				udict[path[i]]= [offset[i],udict[path[i]][1]]
			
			elif (udict[path[i]][0] <= offset[i])  and ( udict[path[i]][1] <= offset[i]+lenght[i]):
                                access+= udict[path[i]][1]-offset[i]
                                udict[path[i]]= [udict[path[i]][0], offset[i]+lenght[i]]
			
			elif ( offset[i] <= udict[path[i]][0] )  and ( udict[path[i]][1] <= offset[i]+lenght[i]):
                                access+= udict[path[i]][1]- udict[path[i]][0]
                                udict[path[i]]= [offset[i], offset[i]+lenght[i]]	
		
			elif ( offset[i]+lenght[i] < udict[path[i]][0] ):
				print "non-match--", i	
		
			elif ( udict[path[i]][1] < offset[i] ):
                                print "non-match--", i
			else:
				print "non-match--", i 
				

	print  "The Reaccess in Bytes: " ,access


def histogram(argv):
	size=24
	matrix = np.zeros((size,size))
 	app_list={}
        udict={}
        source=[]
	for i in xrange(size):
		app_list[i]=[]
        total_access_bytes=0
        fd = open(sys.argv[1], 'r')
        for line in fd:
                value = line.split(" ")
                source.append(value[0])
                value[1]= value[1].replace("[","")
                value[1]= value[1].replace("]","")
		hour = int((value[1].split("T")[1]).split(":")[0])	
	        url = value[2].split("?")
                d_name = url[0].split("celfs/read/")[1]
		#if hour not in app_list:
		#	app_list[hour] = [d_name]
		#else:
		app_list[hour].append(d_name)
	for i in xrange(size):
#		matrix[i,i]=len(app_list[i])
	#	print(matrix)
		#print i,len(app_list[i]), app_list[i]
#		for m in app_list[i]:
#			if m not in udict:
#				matrix[i,i] +=1
		new={}
		for m in app_list[i]:
                        if m not in udict:
                                udict[m]=1
				new[m]=1
		for j in xrange(i,size):
			for k in app_list[j]:
	#			print k , udict
				if (k in new) :
					matrix[i,j] +=1
	#				print(matrix)	
		#for m in app_list[i]:
                 #       if m not in udict:
                  #              udict[m]=1
	print(matrix)
	df = pd.DataFrame(data=matrix.astype(int))
	df.to_csv('histogram_file.csv', sep=' ', header=False, index=False)
	
	fd2 =open("histo.csv" , "w")
	fd2.write(matrix[0,1])
	fd2.close()



if __name__ == "__main__":
	source=[]
        date=[]
        path=[]
        cache=[]
        offset=[]
        lenght=[]
	histogram(sys.argv[1:])
#	source, date, path, lenght, offset ,cache = read_traces(sys.argv[1:])
#	source, date, path, lenght, offset ,cache = histogram(sys.argv[1:])
#	file_reaccess(path,offset,lenght)
#	uniq_files(source, date, path, lenght, offset ,cache)
#	file_size(source, date, path, lenght, offset ,cache)
#	occur(source, date, path, lenght, offset ,cache)




