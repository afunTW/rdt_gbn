#!/usr/bin/python3

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
	dt = rdt(SRCPORT, DESTPORT);
	dt.setMTU(BUFFER_SIZE);	# Guarantee buffer size is greater equal than rdt.MTU

	# init
	ACK = 0
	expectedseqnum = 0;
	sndpkt = dt.make_pkt(0, ACK);

	while True:
		client, address = s.accept();
		is_receiving = True
		count = 0
		while is_receiving:
			try:
				# client, address = s.accept();
				################################## socket
				pkt = client.recv(BUFFER_SIZE);
				################################## socket

				# rdt_rcv(rcvpkt) && !corrupt(rcvpkt) && hasseqnum(rcvpkt, expectedseqnum)
				if dt.corrupt(pkt) is False and dt.hasseqnum(pkt, expectedseqnum) is True:
					count = count + 1;
					print ("Received:", count);
					data = dt.extract(pkt);	# binary string of payload
					# dt.delieverData(data);
					print(dt.showdata(pkt));
					expectedseqnum += 1;
					ACK = (ACK+1)%2;
					sndpkt = dt.make_pkt(expectedseqnum, ACK);

					################################## socket
					client.send(sndpkt);
					print('Sending acksum: ', expectedseqnum);
					################################## socket

				# default
				################################## socket
				else: client.send(sndpkt);
				################################## socket
			except socket.error:
				#here the Sender close the socket
				is_receiving = False
		client.close()

		#client.close()
	s.close()