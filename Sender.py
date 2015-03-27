#!/usr/bin/python3

"""
	1. Get data from upper layer (rdt)
	2. Segmentation (rdt)
	3. Create tcp socket (tcpSocket)
	4. Sending (tcpSocket)
"""
import sys
import binascii

from rdt import *
from tcpSocket import *

if __name__ == '__main__':

	transport = rdt();
	transport.getData("explain");
	transport.segmentation();

	# DEST = 'localhost';
	# DESTPORT = 9999;

	# sender = tcpSocket(8888);	# init will create a socket and random source port
	# sender.connect(DEST, DESTPORT);
	# sender.send('Hello')
	# sender.close();