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
from time import sleep

# rdt global setting
SEQ_DURATION = list([i for i in range(0,6)]);	# Guarantee seq# start from 0
N = int(len(SEQ_DURATION)/2);			# window size

# udt global setting
BUFFER_SIZE = 1024*8;
HOP_COUNT = 10;
DEST = 'localhost';
DESTPORT = 9990;
SRCPORT = 8888;

UDT_SOCKET = None
CORRUPTED_MESSAGE = 'CORRUPTED_MESSAGE_HERE'

def string_to_bin(s):
	r = "".join(format(ord(x), 'b') for x in s)
	return r

def decide_lost():
	i = randint(0,100);
	return True if i > 90 else False

def initialize_socket():
	global UDT_SOCKET
	if UDT_SOCKET is None:
		UDT_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		UDT_SOCKET.connect((DEST, DESTPORT))
		UDT_SOCKET.settimeout(1)

def udt_send(pkt):
	global UDT_SOCKET
	if decide_lost():
		print("---Trigger: data lost---")
		sleep(0.5)
		return

	initialize_socket()
	UDT_SOCKET.send(pkt)

def udt_recv():
	global UDT_SOCKET
	initialize_socket()
	data = None
	try:
		data = UDT_SOCKET.recv(BUFFER_SIZE)
		print('length of udt_recv data: ', len(data))

		#here we simulate corruption
		if decide_lost(): data = flip_bits(data);

		return data
	except socket.timeout: return None;
	except socket.error as e: print("Socket error: ", e);  return None;

def flip_bits(data):
	print("---Trigger: data is flipped---")
	# return string_to_bin(CORRUPTED_MESSAGE)
	return None

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
	sndpkt = list([False for i in range(0,len(SEQ_DURATION))]);
	sndcount = 0

	while sndcount < len(dt.bindatalist)-1:
		data = dt.bindatalist[sndcount];
		print('base: %d, next: %d' % (base_seq, next_seq))
		# rdt_send(data)
		if next_seq < (base_seq + N) :
			print(next_seq, ' in total ', len(sndpkt))
			sndpkt[next_seq] = dt.make_pkt(next_seq, ACK, data);
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
		print()
	udt_channel_close()