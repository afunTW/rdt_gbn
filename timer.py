#!/usr/bin/python3

import sys
import time

class timer():
	def __init__(self):
		if sys.platform == 'win32':
			self.default_timer = time.clock;	# On Windows, the best timer is time.clock
		else:
			self.default_timer = time.time;	# On most other platforms the best timer is time.time
	def settime(self, sec):
		self.set_time = sec;
		print("Set timer: %.3f sec" % self.set_time);
	def start(self):
		self.start_time = self.default_timer();
		print("Start timer");
	def timeout(self):
		return True if self.default_timer()-self.start_time > self.set_time else False;