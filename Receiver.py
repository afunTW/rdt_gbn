#!/usr/bin/python3

import sys
from tcpSocket import *

if __name__ == '__main__':
	DEST = 'localhost';
	DESTPORT = 8888;

	receiver = tcpSocket(9999);
	receiver.connect(DEST, DESTPORT);
	receiver.listen();
	receiver.recv();
	receiver.close();