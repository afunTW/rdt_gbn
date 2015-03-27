#!/usr/bin/python3

import sys
import random

class rdt(object):
	def __init__(self):
		self.infile = None;
		self.MTU = 1024;		# Maximum Transmission Unit, (bytes/ segment)
		self.init_seqNum = None;
		self.next_seqNum = None;
		self.next_ACK = None;
		self.segCounts = None;
		self.pktdict = {};

	# Sender( Client)
	# Get data from upper layer
	def getData(self, filename= None):
		try: self.infile = sys.stdin if filename is None else open(filename, "r");
		except Exception as e: print('Get data error: ', e); raise e;

	def getHeader(self, srcport, destport):
		self.srcport = srcport;
		self.destport = destport;

		srcport = format(self.srcport,'016b')
		destport = format(self.destport, '016b')

	def setMTU(self, MTU):
		try: self.MTU = MTU;
		except Exception as e: print('Set MTU error: ', e); raise e;

	def setSeqNum(self, num):
		try: self.init_seqNum = num;
		except Exception, e: print('Set initial sequence number error: ', e); raise e;

	# Sender( Client)
	def segmentation(self):
		# Split the data into a list of char, and call sys.getsizeof() to calculate bytes
		charlist = list(list(ch for ch in line) for line in list(self.infile))
		totalsize = sum(sum(sys.getsizeof(j) for j in i) for i in charlist)
		segCounts = int(totalsize/self.MTU) + (1 if totalsize%self.MTU > 0 else 0)
		if self.init_seqNum == None: self.init_seqNum = random.randint(1, 100)

		print("Total size of %s: %d" % (self.infile.name, totalsize))
		print("Maximum Transmission Unit: ", self.MTU);
		print("Create %d segments from seq# %d to seq# %d" % (segCounts, self.init_seqNum, self.init_seqNum+segCounts))

		# Segmentation

	# Receiver( Server)
	# def reassembly(self, seqdata):