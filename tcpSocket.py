#!/usr/bin/python3

import sys
import socket
import random

class tcpSocket(object):
	def __init__(self, srcport= None):
		if srcport is None: self.srcport = random.randint(8000, 40000);
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	# IPv4, TCP stream
		print('TCP socket create');
		# self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
		# self.sock.settimeout(None);	# 0: non-blocking, None: blocking
		self.sock.bind(('', srcport));
		print('TCP socket bind');

	def connect(self, dest, port):
		self.dest = dest;
		self.destport = port;
		try: self.sock.connect((dest, port)); print('TCP socket connect')
		except Exception as e: print('Unable to connect.\nError: ', e);

	def close(self):
		try: self.sock.close();
		except Exception as e: print('Close error: ', e);

	# Receivver( Server)
	def listen(self, hopCount=1):
		self.sock.listen(hopCount);
		print('TCP socket listen on %d hop' % hopCount);

	# Sender( Client)
	def send(self, data):
		for seg in data:
			try: self.sock.send(bytes(seg, 'utf-8'));
			except Exception as e: print('Sendling error: ', e);

	# Receiver( Server):
	def recv(self, bufferlength=1024):
		try: self.sock.recv(bufferlength);
		except Exception as e: print('Receive error: ', e);