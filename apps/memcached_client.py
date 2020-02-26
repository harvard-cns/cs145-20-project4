import memcache
import time
import sys
from utils import measure_time, wait_util
from memcached_trace import MemcachedTrace

class Client:
	def __init__(self, start_time, actions, server_ip):
		self.start_time = start_time
		self.actions = actions
		self.mc = memcache.Client(map(lambda ip: ip + ":11211", server_ip), debug=0)
	def work(self):
		for action in self.actions:
			latency = self.execute(action)
			print "%lf %.0lf"%(action.time, latency * 1e6) # us
	def execute(self, action):
		wait_util(self.start_time + action.time)
		if action.func == 0:
			return measure_time(lambda : self.mc.set(action.key, action.value))
		else:
			return measure_time(lambda : self.mc.get(action.key))
def read_traffic_file(host_name, traffic_file):
	actions = []
	with open(traffic_file, "r") as file:
		lines = file.readlines()
		server_ip = lines[0].strip().split(' ') # first line is the memcached server IPs
		for line in lines[1:]: # rest of the file are actions
			tokens = line.strip().split(' ') # host_name, time, func, key[, value]
			if tokens[0] != host_name:
				continue
			if tokens[2] == "0": # set: time, func, key, value
				actions.append(MemcachedTrace(float(tokens[1]), 0, tokens[3], tokens[4]))
			else: # get: time, func, key
				actions.append(MemcachedTrace(float(tokens[1]), 1, tokens[3]))
	return server_ip, actions

if __name__ == "__main__":
	if len(sys.argv) != 4:
		print "usage: python memcached_client.py <start_time> <host_name> <traffic_file>"
		sys.exit(1)
	start_time = float(sys.argv[1]) # we indicate a global start time
	host_name = sys.argv[2]
	traffic_file = sys.argv[3]

	# use host_name to find the actions
	server_ip, actions = read_traffic_file(host_name, traffic_file)
	client = Client(start_time, actions, server_ip)
	client.work()
