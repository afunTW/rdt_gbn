#!/usr/bin/python3

import sys
import random

from rdt import *
from timer import *

# rdt global setting
SEQ_DURATION = list([i for i in range(0,6)]);	# Guarantee seq# start from 0
N = int(len(SEQ_DURATION)/2);			# window size

# udt global setting
BUFFER_SIZE = 1024*8;
HOP_COUNT = 10;
DEST = 'localhost';
DESTPORT = 9990;
SRCPORT = 8888;
UDT_SOCKET = None;

def decide_lost(pkt): return pkt_lost(pkt) if random.randint(0,100) > 80 else pkt;
def decide_flip(pkt): return flip_bits(pkt) if random.randint(0,100) > 80 else pkt;

def pkt_lost(pkt):
	print("############### Trigger: data lost");
	time.sleep(0.5);
	return None;

def flip_bits(pkt):
	print("############### Trigger: data is flipped");
	datatransfer = rdt(SRCPORT, DESTPORT);
	pkt = datatransfer.extract(pkt);
	isflip = random.randint(0,len(pkt));
	tmplist = list(pkt.decode('utf-8'));
	tmplist[isflip] = '1' if tmplist[isflip] == '0' else '0';
	return bytes(''.join(tmplist), 'utf-8')

def initialize_socket():
	global UDT_SOCKET
	if UDT_SOCKET is None:
		UDT_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		UDT_SOCKET.connect((DEST, DESTPORT))
		UDT_SOCKET.settimeout(1)

def udt_send(pkt):
	pkt = decide_lost(decide_flip(pkt));
	initialize_socket();
	if pkt is not None: UDT_SOCKET.send(pkt);

def udt_recv():
	global UDT_SOCKET
	initialize_socket()
	try:
		pkt = UDT_SOCKET.recv(BUFFER_SIZE);
		return decide_lost(pkt);
	except socket.timeout: return None;
	except socket.error as e: print("Socket error: ", e);  return None;

#close the channel so that the receiver can take another connect
def udt_channel_close():
	global UDT_SOCKET
	if UDT_SOCKET is not None:
		UDT_SOCKET.close()
		UDT_SOCKET = None

if __name__ == '__main__':

	t = timer();
	t.settime(0.2);	# sec
	dt = rdt(SRCPORT, DESTPORT);
	dt.setMTU(int(BUFFER_SIZE/8));	# Guarantee buffer size is greater equal than rdt.MTU
	dt.getData("explain.txt");
	dt.segmentation();

	# Manage corresponding seq# and sending packet
	ACK = 0;
	base_seq = 0
	next_seq = 0
	sndpkt = list([False for i in range(0,dt.pktcount)]);

	while base_seq < len(dt.bindatalist):
		if next_seq < len(dt.bindatalist): data = dt.bindatalist[next_seq];
		else: data = None; sndpkt.append(False);

		# rdt_send(data)
		if next_seq < (base_seq + N) :
			sndpkt[next_seq] = dt.make_pkt(next_seq, ACK, data);
			################################## socket
			print('\nsend pkt', 'seq#: ', next_seq);
			udt_send(sndpkt[next_seq]);
			################################## socket
			if next_seq == base_seq: t.start();
			next_seq += 1;

		# timeout
		if t.timeout() is True:
			print('Timeout!!!'); t.start();	#restart timer for base_seq pkt
			for i in range(base_seq, next_seq):	# resend all unreceived packet in window
				################################## socket
				print('send seq= %d pkt in timeout' % i)
				udt_send(sndpkt[i]);
				################################## socket

		# rdt_rcv(rcvpkt) && !corrupt(rcvpkt)
		################################## socket
		rcvpkt = udt_recv();
		if rcvpkt is None: continue;
		################################## socket
		if rcvpkt and dt.corrupt(rcvpkt) is False:
			print('packet received, get acksum: ', dt.getacksum(rcvpkt))
			base_seq = dt.getacksum(rcvpkt);
			ACK = (ACK+1)%2;
			if base_seq != next_seq: t.start();	# restart timer for base_seq pkt
	udt_channel_close()