#!/usr/bin/python3

import sys
import socket
import asyncio

import checksum as cs

################################################################################
# Reliable data transfer
################################################################################
class rdt(object):
	def __init__(self, srcport, destport):
		self.infile = None;
		self.MTU = 1024;		# Maximum Transmission Unit, (bytes/ segment)
		self.pktcount = None;
		self.datalist=[];		# list of seperate data
		self.bindatalist=[];# list of corresponding binary string by datalist

		self.srcport = srcport;
		self.destport = destport;

	"""
		Get/ Deliever data from/ to upper layer
	"""
	def getData(self, filename= None):
		try: self.infile = sys.stdin if filename is None else open(filename, "r");
		except Exception as e: print('Get data error: ', e); raise e;
	def delieverData(self, filename= None):
		if filename is None: sys.stdout.write(self.outfile);
		else: f = open(filename, "w"); f.write(self.outfile);

	def segmentation(self):
		# Split the data into a list of char
		charlist = list(list(ch for ch in line) for line in list(self.infile))
		charlist = [ch for block in charlist for ch in block]
		# datatotalbytes = sum(sys.getsizeof(i) for i in charlist)
		datatotalbytes = len(charlist)*2	# bytes
		self.pktcount = int(datatotalbytes/self.MTU) + (1 if datatotalbytes%self.MTU > 0 else 0)

		print("Total size of %s: %d (bytes)" % (self.infile.name, datatotalbytes));
		print("Maximum Transmission Unit (bytes) : ", self.MTU);
		print("Create %d segments" % self.pktcount);

		# Segmentation, assume MTU is even number
		header_bits = 112;
		databits = (self.MTU*8) - header_bits;	# bits
		bincharlist = [cs._16bin(ord(i)) for i in charlist]

		for i in range(0, len(bincharlist), int(databits/16)):
			self.datalist.append(charlist[i:i+int(databits/16)])
			self.bindatalist.append(bincharlist[i:i+int(databits/16)])

	def make_pkt(self, seqnum, ack, data=None, encode='utf-8'):
		print("seq= %d, ack= %d" % (seqnum, ack));
		header = cs._16bin(self.srcport)+cs._16bin(self.destport)+ cs._32bin(seqnum)+ cs._32bin(ack)
		if data is not None:
			bytesdata = bytes();
			for i in range(0, len(data)): bytesdata += bytes(data[i], encode);
			check = cs.generate_checksum(header + cs._binstring(bytesdata.decode(encode)));
			return bytes(header+check, encode)+bytesdata;
		else: return bytes(header + cs.generate_checksum(header), encode);

	# Show the data in the bytes packet
	def showdata(self, packet):
		data = cs.getpayload(packet.decode('utf-8'));
		datalist = [];
		for i in range(0,len(data), 16):
			chunk = chr(int(str(data[i:i+16]), 2));
			datalist.append(chunk);
		return datalist;

	def setMTU(self, MTU):
		try: self.MTU = MTU;
		except Exception as e: print('Set MTU error: ', e); raise e;
	def corrupt(self, packet, encode='utf-8'):
		return False if cs.valid_ckecksum(packet, encode) is True else True;
	def getacksum(self, packet):
		return int(cs.getseq(packet), 2);
	def hasseqnum(self, rcvpkt, expectedseqnum):
		return True if int(cs.getseq(rcvpkt), 2) == expectedseqnum else False;
	def is_mypkt(self, receivepacket):
		return True if int(cs.getdestport(receivepacket), 2) == self.srcport else False;
	def extract(self, packet):
		return cs.getpayload(packet);