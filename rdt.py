#!/usr/bin/python3

import sys
import random

import checksum

class rdt(object):
	def __init__(self, srcport, destport):
		self.infile = None;
		self.MTU = 1024;		# Maximum Transmission Unit, (bytes/ segment)
		self.init_seqN = None;
		self.next_ACK = None;
		self.pktcount = None;

		self.datalist=[];		# list of seperate data
		self.seqNlist=[];		# list of corresponding seq number with datalist
		self.bindatalist=[];# list of corresponding binary string by datalist

		try: self.srcport = srcport; self.destport = destport;
		except Exception as e: print('Error: ', e);

		if self.next_ACK == None: self.next_ACK = random.randint(1, 100);
		self.checksum = checksum._16bin(0);

	# Sender( Client)
	# Get data from upper layer
	def getData(self, filename= None):
		try: self.infile = sys.stdin if filename is None else open(filename, "r");
		except Exception as e: print('Get data error: ', e); raise e;

	def delieverData(self, filename= None):
		if filename is None: sys.stdout.write(self.outfile);
		else: f = open(filename, "w"); f.write(self.outfile);

	def setMTU(self, MTU):
		try: self.MTU = MTU;
		except Exception as e: print('Set MTU error: ', e); raise e;

	def setSeqNum(self, num):
		try: self.init_seqN = num;
		except Exception as e: print('Set initial sequence number error: ', e); raise e;

	# Sender
	def segmentation(self):
		# Split the data into a list of char
		charlist = list(list(ch for ch in line) for line in list(self.infile))
		charlist = [ch for block in charlist for ch in block]
		# datatotalbytes = sum(sys.getsizeof(i) for i in charlist)
		datatotalbytes = len(charlist)*2	# bytes
		pktcount = int(datatotalbytes/self.MTU) + (1 if datatotalbytes%self.MTU > 0 else 0)
		if self.init_seqN == None: self.init_seqN = random.randint(1, 100)

		print("Total size of %s: %d (bytes)" % (self.infile.name, datatotalbytes));
		print("Maximum Transmission Unit (bytes) : ", self.MTU);
		print("Create %d segments" % pktcount);

		# Segmentation, assume MTU is even number
		header_bits = 112;	# srcport(16)+ destport(16)+ seqnum(32)+ ACK(32)+ checksum(16)(bits)
		databits = (self.MTU*8) - header_bits;	# bits
		bincharlist = [checksum._16bin(ord(i)) for i in charlist]
		next_seqNum = self.init_seqN;

		for i in range(0, len(bincharlist), int(databits/16)):
			self.datalist.append(charlist[i:i+int(databits/16)])
			self.bindatalist.append(bincharlist[i:i+int(databits/16)])
			self.seqNlist.append(next_seqNum);
			next_seqNum += int(databits/8);

	# Receiver( Server)
	# def reassembly(self, seqdata):

	def make_pkt(self, seqnum, data):
		print("seq= %d, ack= %d" % (seqnum, self.next_ACK));

		header = checksum._16bin(self.srcport)+checksum._16bin(self.destport)+ checksum._16bin(seqnum)+ checksum._16bin(self.next_ACK)
		data = checksum._16bin(int(''.join(data), 2));	# convert list to string then pass to function
		check = checksum.generate_checksum(header + data);

		return header+check+data

	# def gbn_send(seld, data):