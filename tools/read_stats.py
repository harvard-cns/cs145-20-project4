#!/usr/bin/env python

from p4utils.utils.topology import Topology
from p4utils.utils.sswitch_API import SimpleSwitchAPI
import sys
import os
import time
import signal
import stats
from threading import Event
from bwstats import BandwidthStats, QlenStats

f_qlen = {}

def handler(signum, frame):
	for link in f_qlen:
		f_qlen[link].close()
	sys.exit("exit...")

class ReadCounters(object):
	# initialize register reader
	def __init__(self, sw_name):
		self.topo = Topology(db="./topology.db")
		self.sw_name = sw_name
		self.thrift_port = self.topo.get_thrift_port(sw_name)
		self.controller = SimpleSwitchAPI(self.thrift_port)

	def get_qlen(self):
		qlens = []
		packets = []
		for i in range(1, 5):
			# controller.register_read can read a certain register with specific index
			# Here we read register from index 1 to 4,
			# because in P4 implementation,
			# We put the queue length data and packets data of the i-th port
			# into the register with index i
			packets.append(self.controller.register_read("in_port_packets", i))
			qlens.append(self.controller.register_read("in_port_qlen", i))
		return (packets, qlens)

if __name__ == "__main__":

	signal.signal(signal.SIGINT, handler)

	# Example, we focus on switch t1
	# which connects to host h1 and h2
	handler = ReadCounters("t1")

	links = ["t1-h1", "t1-h2"]

	# For each link, we maintain its # packets and sum of queue length 
	last_qlen = {}
	last_packets = {}
	f_qlen = {}

	# We write data into files for each link
	for link in links:
		last_qlen[link] = 0
		last_packets[link] = 0
		f_qlen[link] = open("./data/qlen_%s.txt" % link, "w")

	count = 0

	while(True):
		count += 1
		
		# get register data
		res = handler.get_qlen()
		packets = res[0]
		qlens = res[1]

		# write the data
		# Here qlens[0] means queue length info in port 1 of switch t1, which is the link t1-h1
		print >> f_qlen["t1-h1"], "%d %f" % (count, (qlens[0] - last_qlen["t1-h1"]) / float(packets[0] - last_packets["t1-h1"]))
		last_qlen["t1-h1"] = qlens[0]
		last_packets["t1-h1"] = packets[0]

		# qlens[1] means queue length info in port 2 of switch t1, which is the link t1-h2
		print >> f_qlen["t1-h2"], "%d %f" % (count, (qlens[1] - last_qlen["t1-h2"]) / float(packets[1] - last_packets["t1-h1"]))
		last_qlen["t1-h1"] = qlens[1]
		last_packets["t1-h1"] = packets[1]

		# Period
		time.sleep(0.1)

