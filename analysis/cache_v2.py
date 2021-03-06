
import sys
import numpy as np
import operator
import pandas as pd
from collections import deque
from lru import LRU
import ConfigParser
import lfucache.lfu_cache as LFU
import logging
##############################################################
## GLobal Variables
#-----------------------------
key=[]
osize=[]
dict={}

config = ConfigParser.ConfigParser()
config.readfp(open('config.ini'))
log_file = config.get('My Section', 'log_file')
logging.basicConfig(filename=log_file,level=logging.DEBUG)


## Parsing the input file
## Get object ID,size and calculate footprint of
## input data for calculating the cache size, 
#----------------------------------------------

#{"remote-addr":"127.0.0.1","user-principal":"-","date":"2018-02-02T16:51:07.004Z","method":"GET","url":"https://celfs.cfsrs1rs92.dft.twosigma.com:10012/celfs/locatecel/dcat?cel=0_26833&pid=1091&path=3","http-version":"1.1","status":"200","content-length":"244","user-agent":"CelFS/20171212.2 Java (app=com.twosigma.simulator.PrefsSimRun,module=ts_pithos_sys_core,pid=967,realm=CB.TWOSIGMA.COM)","request-time":"1","cache-hit":"CacheHit","cache-time":"1","cache-reason":"ok","cache-hit-local-chunks":"1","cache-hit-non-local-chunks":"-","cache-hit-local-bytes":"810","cache-hit-non-local-bytes":"-","cache-timing":"cipherGet=-90376,firstChunkRead=55,followingChunks=1,decrypt=0","response-time":"0.53596","pid":"28851","keyserver-details":"keyUseCounter=0,keyserversKnown=0,keyserverShuffleCount=0,keyserverUrl=,knownStorageInstances=1521,keySizeKnown=-1,wasHotCache=1"}


def parse(fname):
        fd = open(fname, 'r')
        data=0
        hit=miss=0
	counter=0
	for line in fd:
		counter+=1
                value = line.split(",")
		print value
		break;
                key1 = value[2]
                osize.append(int(key1.split("length=")[1]))
                key.append(key1)
                if key1 not in dict:
                        dict[key1]=1
                        data+=int(key1.split("length=")[1])
			miss+=int(key1.split("length=")[1])
		else:
			hit+=int(key1.split("length=")[1])
#		if(warmup <miss ):
#			print counter
#			print miss, hit, warmup
#			break; 
        fd.close()
	dict.clear()
	logging.info("Footprint " + str(data))
	logging.info("Hit " + str(hit))
	logging.info("Miss " + str(miss))
	print hit, miss
	return data
## FIFO eviction policy
#-----------------------------
def fifo(ratio,output_file,data):
	hit=miss=0
	size = avail = float(data * ratio)/100
	hashmap={}
	avail=int(avail)
	fifo=deque()
	for i in range(len(key)):
		if key[i] in hashmap:
			if(i>14915099):
				hit+=int(hashmap[key[i]])
		else:
			if(i>14915099):
				miss += int(osize[i])
			if (osize[i] <= avail):
				fifo.append(key[i])
				hashmap[key[i]]=osize[i]
				avail -= osize[i]
			else:
				while(osize[i] > avail):
					id=fifo.popleft()
					avail+=hashmap[id]
					del hashmap[id]
				hashmap[key[i]]=osize[i]
				fifo.append(key[i])
				avail -= osize[i]



	fd = open("fifo.res","a")
        fd.write(str(hit)+","+str(miss)+"\n")
        fd.close()
        logging.info("Hit Ratio:"+str(hit))
        logging.info("Miss Ratio:"+str(miss))

       # print "Cache Size:", int(size)
       # print "Cache Size Ratio:", ratio/10
        print "Hit Ratio:", hit
        print "Miss Ratio:", miss


def lru(ratio,output_file,data):
	hit=miss=0
        #size = avail = float(data * ratio)/100
   	#divi=math.pow(2,ratio)
 	size = avail = ratio*1024*1024*1024*1024
	#size = float(data)/divi
        hashmap={}
        avail=int(avail)
	cache = LRU(82170872)
	for i in range(len(key)):
		if key[i] in hashmap:
	#		if(i>14915099):
	#			hit+=int(osize[i])
			hit+=int(osize[i])
			cache[key[i]]=osize[i]
		else:
		#	if(i>14915099):
		#		miss +=int(osize[i])
			miss +=int(osize[i])
			if (int(osize[i]) <= avail):
				cache[key[i]]="1"
				hashmap[key[i]]=int(osize[i])
				avail -= int(osize[i])
			else:
				while(int(osize[i]) > avail):
					id = cache.peek_last_item()[0]	
				 	avail+=int(hashmap[id])
                                        del cache[id]
					del hashmap[id]
				hashmap[key[i]]=osize[i]
                                cache[key[i]]="1"
                                avail -= int(osize[i])
        fd = open("lru.res","a")
        fd.write(str(hit)+","+str(miss)+"\n")
        fd.close()
        logging.info("Hit Ratio:"+str(hit))	
        logging.info("Miss Ratio:"+str(miss))	
#	print hit, "," , miss
	print float(miss)/float(hit+miss)

def lfu(ratio,output_file,data):
	hit=miss=0
        size = avail = float(data * ratio)/100
        hashmap={}
        avail=int(avail)
	cache = LFU.Cache()
	for i in range(len(key)):
                if key[i] in hashmap:
			if(i>14915099):
				hit+=int(osize[i])
			cache.access(key[i])
		else:
			if(i>14915099):
				miss+=int(osize[i])
			if (int(osize[i]) <= avail):
                        	cache.insert(key[i],"a")
                                hashmap[key[i]]=int(osize[i])
                                avail -= int(osize[i])
			else:
				while(int(osize[i]) > avail):
					id = cache.get_lfu()[0]
					avail+=int(hashmap[id])
					cache.delete_lfu()
					del hashmap[id]
	 			hashmap[key[i]]=osize[i]
				cache.insert(key[i],"a")
				avail -= int(osize[i])
        fd = open("lfu.res","a")
        fd.write(str(hit)+","+str(miss)+"\n")
        fd.close()
        logging.info("Hit Ratio:"+str(hit))
        logging.info("Miss Ratio:"+str(miss))
        print hit, "," , miss


if __name__ == "__main__":

## Load the configuration filec
#------------------------------
	input_file = config.get('My Section', 'input_file')	
	cache_size= config.get('My Section', 'cache_size')
	cache_type = config.get('My Section', 'cache_type')
	output_file = config.get('My Section', 'output_file')


## Parsing the Input File
	logging.info('**************************')
	logging.info('Parsing ' + str(input_file))
	data=parse(input_file)

# Running Single Level Cache
	if cache_type == "fifo":
		logging.info('Eviction Policy: FIFO' )
		for i in xrange(1,size_ratio+1):
			fifo(i, output_file,data)
	if cache_type =="lru":
		logging.info('Eviction Policy: LRU' )
		for i in xrange(1,size_ratio+1):
		liste=[0.2,0.3,0.4]
       	
		for i in liste:
			lru(i, output_file,data)
       	
	elif cache_type =="lfu":
               logging.info('Eviction Policy: LFU' )
                for i in xrange(1,size_ratio+1):
                        lfu(i, output_file,data)
       	
  	#test(sys.argv[1:])
