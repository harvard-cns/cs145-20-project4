import numpy as np
import random as rdm
import string
import sys

memcached_traces = []
iperf_traces = []

memcached_keys = []

def get_random_string(size):
	return ''.join(rdm.choice(string.ascii_letters + string.digits) for x in range(size))

def gen_memcached_trace():
	p = rdm.uniform(0, 1)
	if p <= 0.5 or len(memcached_keys) == 0:
		if p <= 0.25 or len(memcached_keys) == 0:
			key = get_random_string(8)
			memcached_keys.append(key)
			value = rdm.randint(0, 65535)
			return key, value
		else:
			idx = rdm.randint(0, len(memcached_keys) - 1)
			key = memcached_keys[idx]
			value = rdm.randint(0, 65535)
			return key, value
	else:
		idx = rdm.randint(0, len(memcached_keys) - 1)
		key = memcached_keys[idx]
		value = -1
		return key, value

def gen_memcached(host_list, length):
	if len(host_list) == 0:
		return
	next_req = 0
    
	next_req = next_req + np.random.poisson(100)
	while next_req < length:
		host = host_list[rdm.randint(0, len(host_list) - 1)]
		burst = np.random.zipf(1.5)
		if burst > 1000:
			burst = 1000
                burst = burst / 500 + 1
		for i in range(burst):
			key, value = gen_memcached_trace()
			memcached_traces.append((next_req, host, key, value))
		next_req = next_req + np.random.poisson(100)

def gen_iperf(host_list, length):
	if len(host_list) == 0:
		return
	next_req = 0

	next_req = next_req + np.random.poisson(2000)
	while next_req < length:
		src = host_list[rdm.randint(0, len(host_list) - 1)]
		dst = host_list[rdm.randint(0, len(host_list) - 1)]
		while dst == src:
			dst = host_list[rdm.randint(0, len(host_list) - 1)]
		burst = rdm.randint(1000, 8000)
		iperf_traces.append((next_req, src, "10.0.0.%d" % dst, burst))
		next_req = next_req + np.random.poisson(2000)

def parse_hosts(hosts_string):
	host_list = []
	if hosts_string == "0":
		return host_list
	hosts = hosts_string.split(',')
	for host_set in hosts:
		if '-' in host_set:
			hlist = host_set.split('-')
			h_start = int(hlist[0])
			h_end = int(hlist[1])
			for host in range(h_start, h_end + 1):
				host_list.append(host)
		else:
			host_list.append(int(host_set))
	return host_list

if __name__ == "__main__":
	if len(sys.argv) != 6:
		print("usage: python generate_trace.py [hosts running memcached servers] [hosts running memcached] [hosts running iperf] [trace length (sec)] [trace file name]")
		print("\thosts running memcached: the list of hosts running memcached. If you want to run memcached on h1, h2, h3, h5, h7, h8, type 1-3,5,7-8 here. No space allowed.")
		print("\thosts running iperf: the format is the same as above.")
		print("\ttrace length (sec): how long do you want to generate this trace.")
		print("\ttrace file name: the output trace file name.")
		exit()

	mc_hosts_server = sys.argv[1]
	mc_hosts_string = sys.argv[2]  
	iperf_hosts_string = sys.argv[3]     
	length = int(sys.argv[4]) * 1000

	mc_server_list = parse_hosts(mc_hosts_server)
	mc_host_list = parse_hosts(mc_hosts_string)
	iperf_host_list = parse_hosts(iperf_hosts_string)

	#if len(mc_host_list) < 2 or len(iperf_host_list) < 2:
	#    exit("Number of hosts must be larger than 1!")

	gen_memcached(mc_host_list, length)
	gen_iperf(iperf_host_list, length)

	traces = memcached_traces + iperf_traces
	traces.sort()

	f = open(sys.argv[5], "w")
	for i in mc_server_list:
		f.write("10.0.0.%d " % i)
	f.write("\n")

	for trace in traces:
		f.write("h%d " % trace[1])
		f.write("%f " % (trace[0] / 1000.0))
		if "." in trace[2]:
			f.write("2 %s %f\n" % (trace[2], trace[3] / 1000.0))
		else:
			if trace[3] == -1:
				f.write("1 %s\n" % trace[2])
			else:
				f.write("0 %s %d\n" % (trace[2], trace[3]))

