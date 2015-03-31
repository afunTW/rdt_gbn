#!/usr/bin/python3

def _16bin(msg):
	return format(msg, '016b');

def generate_checksum(data):
	check = 0;
	for i in range(0,len(data), 16):
		check += int(data[i:i+16], 2);

	# Guarantee the check binary string have exactly 16 bits
	check = _16bin(check);
	check = check[-16:]

	return format(int(check,2)^0xffff, '016b');	# 1's complement

def valid_ckecksum(pkt):
	checksum = getchecksum(pkt);
	data = pkt[0:96]+pkt[112:];
	return True if generate_checksum(data) == checksum else False;

def getsrcport(pkt): return pkt[0:16];
def getdestport(pkt): return pkt[16:32];
def getseq(pkt): return pkt[32:64];
def getack(pkt): return pkt[64:96];
def getchecksum(pkt): return pkt[96:112];
def getpayload(pkt): return pkt[112:];
def getheader(pkt): return pkt[0:112];