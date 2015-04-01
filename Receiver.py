#!/usr/bin/python3

"""
	1. Create tcp socket, bind, connect, listen
	2. Receive the first empty packet
	3. Get the S_seq# and S_ack
	4. Sending R_seq# and R_ack
	5. Check checksum, send ack back
	6. Seperate packet into segment, deliever to upper layer
"""
import sys

from rdt import *
from tcpSocket import *

BUFFER_SIZE = 1024;

if __name__ == '__main__':
	DEST = 'localhost';
	DESTPORT = 8888;
	SRCPORT = 9999;

	# receiver = tcpSocket(9999);
	# receiver.connect(DEST, DESTPORT);
	# receiver.listen();
	# receiver.recv();

	dt = rdt(SRCPORT, DESTPORT);
	dt.setMTU(BUFFER_SIZE);	# Guarantee buffer size is greater equal than rdt.MTU

	# init
	ACK = 0
	expectedseqnum = 0;
	sndpkt = dt.make_pkt(0, ACK);

	while True:
		################################## socket
		pkt = udt_recv(BUFFER_SIZE);
		################################## socket

		# rdt_rcv(rcvpkt) && !corrupt(rcvpkt) && hasseqnum(rcvpkt, expectedseqnum)
		if dt.corrupt(pkt) is False and dt.hasseqnum(pkt, expectedseqnum) is True:
			data = dt.extract(pkt);	# binary string of payload
			dt.delieverData(data);
			sndpkt = make_pkt(expectedseqnum, ACK);

			################################## socket
			udt_send(sndpkt);
			################################## socket

			expectedseqnum += 1;
			ACK = (ACK+1)%2;

		# default
		################################## socket
		udt_send(sndpkt);
		################################## socket

	# receiver.close();