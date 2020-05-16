import socket
import threading
import time
import sys
import Queue
import random
from utils import wait_util
from iperf_trace import IperfTrace

PORT = 5001

class IperfClient:
	def __init__(self, start_time, traffics):
		self.start_time, self.traffics = start_time, traffics
		self.buf = 'x' * 500000
	def work(self):
		th = []
		q = Queue.Queue()
		for traffic in self.traffics:
			t = threading.Thread(target = self.execute, args = (traffic,q))
			th.append(t)
			t.start()
		for t in th:
			t.join()
		while not q.empty():
			traffic,bps = q.get()
			print bps
	def execute(self, traffic, q):
		byte = 0
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# port = random.randint(5001, 5100)
		addr = (traffic.dst_ip, PORT)
		PORT += 1
		sock.connect(addr)
		# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# addr = (traffic.dst_ip, PORT)

		end_time = self.start_time + traffic.time + traffic.duration
		wait_util(self.start_time + traffic.time)
		start = time.time()
		now = start
		while now < end_time:
			byte += sock.send(self.buf)
			#for i in range(500):
			#	byte += sock.sendto(self.buf, addr)
			#time.sleep(0.001)
			now = time.time()
		ret = float(byte) / (now - start) * 8
		q.put((traffic,ret))
		return ret

def read_traffic_file(host_name, traffic_file):
	traffics = []
	with open(traffic_file, "r") as file:
		lines = file.readlines()
		for line in lines[1:]:
			tokens = line.strip().split(' ') # host_name, time, func, dst_ip, duration
			if tokens[0] != host_name:
				continue
			if tokens[2] != '2': # filter out non-iperf traffic
				continue
			traffics.append(IperfTrace(float(tokens[1]), tokens[3], float(tokens[4])))
	return traffics

if __name__ == "__main__":
	if len(sys.argv) != 4:
		print "usage: python iperf_client.py <start_time> <host_name> <traffic_file>"
		sys.exit(1)
	start_time = float(sys.argv[1]) # we indicate a global start time
	host_name = sys.argv[2]
	traffic_file = sys.argv[3]

	# use host_name to find the traffic
	traffics = read_traffic_file(host_name, traffic_file)
	client = IperfClient(start_time, traffics)
	client.work()
