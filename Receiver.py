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

BUFFER_SIZE = 1024*8;
HOST = '';
DEST = 'localhost';
DESTPORT = 8888;
SRCPORT = 9990;

if __name__ == '__main__':
	# socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
	s.bind((HOST, SRCPORT));
	s.listen(1);

	# rdt
	dt = rdt(SRCPORT, DESTPORT, 'server');
	dt.setMTU(BUFFER_SIZE);	# Guarantee buffer size is greater equal than rdt.MTU

	# init
	ACK = 0
	expectedseqnum = 0;
	sndpkt = dt.make_pkt(0, ACK, encode= 'utf-8');

	while True:
		client, address = s.accept();
		################################## socket
		print('Receive pkt: ')
		pkt = client.recv(BUFFER_SIZE)
		print(dt.showdata(pkt));
		################################## socket

		# rdt_rcv(rcvpkt) && !corrupt(rcvpkt) && hasseqnum(rcvpkt, expectedseqnum)
		if dt.corrupt(pkt) is False and dt.hasseqnum(pkt, expectedseqnum) is True:
			data = dt.extract(pkt);	# binary string of payload
			# dt.delieverData(data);
			print(dt.showdata(sndpkt));
			sndpkt = dt.make_pkt(expectedseqnum, ACK, encode= 'utf-8');

			################################## socket
			print('send ack back')
			print(dt.showdata(sndpkt));
			client.send(sndpkt);
			################################## socket

			expectedseqnum += 1;
			ACK = (ACK+1)%2;

		# default
		################################## socket
		print('default sending')
		dt.showdata(sndpkt)
		client.send(sndpkt);
		################################## socket

		client.close()
	s.close()