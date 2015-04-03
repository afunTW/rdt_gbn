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

def decide_lost():
	i = randint(0,100)
	print('decide_lost: ', (True if i>10 else False))
	return True if i>10 else False

def udt_send(pkt):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((DEST, DESTPORT))
		s.send(pkt);
		s.close();
	except Exception as e: print('udt_send socket error: ', e)

def udt_recv():
	# if decide_lost() is True: return None;
	 # else:
	print('---Enter udt_recv else---');
	try:
		print('---Enter udt_recv try---');
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
		print('Create a socket');
		s.connect((DEST, DESTPORT));
		print('Sockket connect')
		print('start to udt_recv')
		data = s.recv(BUFFER_SIZE)
		print('end of udt_recv')
		s.close()
	except Exception as e: print('udt_recv socket error: ', e)
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

		# rdt_send(data)
		if next_seq < (base_seq + N) :
			sndpkt[next_seq] = dt.make_pkt(next_seq, ACK, data, 'utf-8');
			################################## socket
			print('send pkt')
			# print(dt.showdata(sndpkt[next_seq]));
			udt_send(sndpkt[next_seq]);
			################################## socket
			if next_seq == base_seq: t.start();
			next_seq = (next_seq + 1) % len(SEQ_DURATION);
			sndcount += 1;

		# timeout
		if t.timeout() is True:
			print('Timeout!!!'); t.start();	#restart timer for base_seq pkt
			for i in range(base_seq, next_seq):	# resend all unreceived packet in window
				################################## socket
				print('resend pkt in timeout')
				udt_send(sndpkt[i]);
				print(dt.showdata(sndpkt[i]));
				################################## socket

		# rdt_rcv(rcvpkt) && !corrupt(rcvpkt)
		################################## socket
		rcvpkt = udt_recv();
		print('rcvpkt: ' ,rcvpkt)
		################################## socket
		if rcvpkt is not None and dt.corrupt(rcvpkt) is False:
			print('recv ack')
			base_seq = dt.getacksum(rcvpkt) + 1;
			ACK = (ACK+1)%2;
			if base_seq != next_seq: t.start();	# restart timer for base_seq pkt

		print();