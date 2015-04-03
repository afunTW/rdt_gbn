#!/usr/bin/python3

"""
	1. Create tcp socket, bind, connect
	2. Get data from upper layer
	3. Segmentation
	4. Manage seq# and ack#
	5. Sending empty data, S_seq# and S_ack#
	6. Sending a list of packet
	7. Close socket
"""
import sys

from rdt import *
from timer import *
from random import randint

# rdt global setting
SEQ_DURATION = list([i for i in range(0,6)]);	# Guarantee seq# start from 0
N = int(len(SEQ_DURATION)/2);			# window size

# udt global setting
BUFFER_SIZE = 1024*8;
HOP_COUNT = 10;
DEST = 'localhost';
DESTPORT = 9990;
SRCPORT = 8888;

CORRUPTED_MESSAGE = 'CORRUPTED_MESSAGE_HERE'
def string_to_bin(s):
	r = "".join(format(ord(x), 'b') for x in s)
	return r

def decide_lost():
	i = randint(0,100)
	if i > 10:
		return True
	return False

def udt_send(pkt):
	#if decide_lost():
	#	print("The channel has lost the packet.")
	#	return
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((DEST, DESTPORT))
	# s.send(bytes(pkt, 'utf-8'))
	s.send(pkt);
	s.close();

def udt_recv():
	if decide_lost():
		return string_to_bin(CORRUPTED_MESSAGE)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((DEST, DESTPORT))
	data = s.recv(BUFFER_SIZE)
	s.close()
	return data

if __name__ == '__main__':

	t = timer();
	t.settime(0.2);	# sec
	dt = rdt(SRCPORT, DESTPORT, 'client');
	dt.setMTU(int(BUFFER_SIZE/8));	# Guarantee buffer size is greater equal than rdt.MTU
	dt.getData("explain");
	dt.segmentation();

	# Manage corresponding seq# and sending packet
	ACK = 0;
	base_seq = 0
	next_seq = 0
	sndpkt = list([False for i in range(0,N)]);
	sndcount = 0

	while True:
		data = dt.bindatalist[sndcount];
		# print(dt.showdata(data));

		# rdt_send(data)
		if next_seq < (base_seq + N) :
			sndpkt[next_seq] = dt.make_pkt(next_seq, ACK, data, 'utf-8');
			# print(sndpkt[next_seq])
			################################## socket
			print('send pkt')
			# print(dt.showdata(sndpkt[next_seq]));
			udt_send(sndpkt[next_seq]);
			################################## socket
			if next_seq == base_seq: t.start();
			next_seq = (next_seq + 1) % len(SEQ_DURATION);
			sndcount += 1;

		# timeout
		print('default timer: ', t.default_timer())
		if t.timeout() is True:
			print('timeout'); t.start();	#restart timer for base_seq pkt
			for i in range(base_seq, next_seq):	# resend all unreceived packet in window
				################################## socket
				print('resend pkt in timeout')
				udt_send(sndpkt[i]);
				################################## socket

		# rdt_rcv(rcvpkt) && !corrupt(rcvpkt)
		################################## socket
		print('recv pkt')
		rcvpkt = udt_recv();
		################################## socket
		if dt.corrupt(rcvpkt) is False:
			base_seq = dt.getacksum(rcvpkt) + 1;
			ACK = (ACK+1)%2;
			if base_seq != next_seq: t.start();	# restart timer for base_seq pkt