#!/usr/bin/python3

import sys

import checksum as cs

class rdt(object):
	def __init__(self, srcport, destport):
		self.infile = None;
		self.MTU = 1024;		# Maximum Transmission Unit, (bytes/ segment)
		self.pktcount = None;

		self.datalist=[];		# list of seperate data
		self.bindatalist=[];# list of corresponding binary string by datalist

		try: self.srcport = srcport; self.destport = destport;
		except Exception as e: print('Error: ', e);

	# Get data from upper layer
	def getData(self, filename= None):
		try: self.infile = sys.stdin if filename is None else open(filename, "r");
		except Exception as e: print('Get data error: ', e); raise e;

	# Deliever data to upper layer
	def delieverData(self, filename= None):
		if filename is None: sys.stdout.write(self.outfile);
		else: f = open(filename, "w"); f.write(self.outfile);

	def setMTU(self, MTU):
		try: self.MTU = MTU;
		except Exception as e: print('Set MTU error: ', e); raise e;

	# Sender
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
		header_bits = 112;	# srcport(16)+ destport(16)+ seqnum(32)+ ACK(32)+ cs(16)(bits)
		databits = (self.MTU*8) - header_bits;	# bits
		bincharlist = [cs._16bin(ord(i)) for i in charlist]

		for i in range(0, len(bincharlist), int(databits/16)):
			self.datalist.append(charlist[i:i+int(databits/16)])
			self.bindatalist.append(bincharlist[i:i+int(databits/16)])

	def make_pkt(self, seqnum, ack, data=None):
		print("seq= %d, ack= %d" % (seqnum, ack));

		header = cs._16bin(self.srcport)+cs._16bin(self.destport)+ cs._16bin(seqnum)+ cs._16bin(ack)
		if data is not None:
			data = cs._16bin(int(''.join(data), 2));	# convert list to string then pass to function
			check = cs.generate_checksum(header + data);
			return header+check+data;
		else: return	header + cs.generate_checksum(header);

	def corrupt(self, packet):
		return False if cs.valid_ckecksum(packet) is True else True;
	def getacksum(self, packet):
		return int(str(cs.getack(packet)), 2);
	def hasseqnum(self, rcvpkt, expectedseqnum):
		return True if int(str(cs.getseq(packet)), 2) == expectedseqnum else False;
	def extract(self, packet):
		return cs.getpayload(packet);