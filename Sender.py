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

# rdt global setting
SEQ_DURATION = list([i for i in range(0,6)]);	# Guarantee seq# start from 0
N = int(len(SEQ_DURATION)/2);			# window size

# udt global setting
BUFFER_SIZE = 1024;
HOP_COUNT = 10;
DEST = 'localhost';
DESTPORT = 9999;
SRCPORT = 8888;

if __name__ == '__main__':

	# sender = tcpSocket(8888);	# init will create a socket and random source port
	# sender.connect(DEST, DESTPORT);
	# sender.send('Hello')

	t = timer();
	t.settime(1);	# sec
	dt = rdt(SRCPORT, DESTPORT);
	dt.setMTU(BUFFER_SIZE);	# Guarantee buffer size is greater equal than rdt.MTU
	dt.getData("explain");
	dt.segmentation();

	# Manage corresponding seq# and sending packet
	ACK = 0;
	base_seq = 0
	next_seq = 0
	sndpkt = list([False for i in range(0,N)]);
	sndcount = 0

	'''
		# non-blocking problem
	'''
	while True:
		data = dt.bindatalist[sndcount];

		# rdt_send(data)
		if next_seq < (base_seq + N) :
			sndpkt[next_seq] = dt.make_pkt(next_seq, ACK, data);
			print(sndpkt[next_seq])
			################################## socket
			udt_send(sndpkt[next_seq]);
			################################## socket
			if next_seq == base_seq: t.start();
			next_seq = (next_seq + 1) % len(SEQ_DURATION);
			sndcount += 1;

		# timeout
		if t.timeout is True:
			print('timeout'); t.start();	#restart timer for base_seq pkt
			for i in range(base_seq, next_seq):	# resend all unreceived packet in window
				################################## socket
				udt_send(sndpkt[i]);
				################################## socket

		# rdt_rcv(rcvpkt) && !corrupt(rcvpkt)
		################################## socket
		rcvpkt = udt_recv(BUFFER_SIZE);
		################################## socket
		if dt.corrupt(rcvpkt) is False:
			base_seq = dt.getacksum(rcvpkt) + 1;
			ACK = (ACK+1)%2;
			if base_seq != next_seq: t.start();	# restart timer for base_seq pkt

	# sender.close();