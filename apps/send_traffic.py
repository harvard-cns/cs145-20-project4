#!/usr/bin/env python

import collections
from collections import defaultdict
import os
import re
import shutil
import time
import sys
import commands
import math

# h1 and h10 is used for video applications.
HOSTS=["h1", "h2", "h3", "h4", "h5", "h6", "h7", "h8", "h9", "h10", "h11", "h12", "h13", "h14", "h15", "h16"]

MN_PATH='~/mininet'
MN_UTIL=os.path.join(MN_PATH, 'util', 'm')

CmdMemcachedClient = {
	'start': 'python apps/memcached_client.py {start_time} {host_name} {traffic_file} > logs/{host_name}_mc.log 2>/dev/null &',
	'kill': 'sudo pkill "python apps/memcached_client.py" 2>/dev/null'
}

CmdMemcachedServer = {
	'start': 'memcached -u p4 -m 100 >/dev/null 2>&1 &',
	'kill': 'sudo killall memcached 2>/dev/null'
}

CmdIperfClient = {
	'start': 'python apps/iperf_client.py {start_time} {host_name} {traffic_file} > logs/{host_name}_iperf.log 2>/dev/null &',
	'kill': 'sudo pkill "python apps/iperf_client.py" 2>/dev/null'
}

CmdIperfServer = {
	'start': 'iperf -s -u -p 5001 >/dev/null 2>&1 &',
	'kill': 'sudo killall iperf 2>/dev/null'
}

def MnExec(hostName, command):
	cmd = '%s %s %s' % (MN_UTIL, hostName, command)
	os.system(cmd)

def wait_util(t):
	now = time.time()
	if now >= t:
		return
	time.sleep(t - now)

class Experiment:
	def __init__(self, traffic_file, hosts, duration):
		self.traffic_file = traffic_file
		self.hosts = hosts
		self.duration = duration
	def start(self):
		now = time.time()
		print "start iperf and memcached servers"
		for host in self.hosts:
			# host = "h%d"%(i+1)
			self.run_mc_server(host)
			self.run_iperf_server(host)
		print "wait 1 sec for iperf and memcached servers to start"
		time.sleep(1)
		print "start iperf and memcached clients"
		self.start_time = int(now) + 3
		for host in self.hosts:
			# host = "h%d"%(i+1)
			self.run_mc_client(host)
			self.run_iperf_client(host)
		
		print "wait for experiment to finish"
		wait_util(self.start_time + self.duration)
		print "stop everything"
		for host in self.hosts:
			# host = "h%d"%(i+1)
			self.stop_mc_server(host)
			self.stop_mc_client(host)
			self.stop_iperf_server(host)
			self.stop_iperf_client(host)
		print "wait 10 sec to make log flushed"
		time.sleep(10)

	def run_mc_server(self, host):
		MnExec(host, CmdMemcachedServer["start"])
	def stop_mc_server(self, host):
		MnExec(host, CmdMemcachedServer["kill"])
	def run_mc_client(self, host):
		MnExec(host, CmdMemcachedClient["start"].format(start_time = self.start_time, host_name = host, traffic_file = self.traffic_file))
	def stop_mc_client(self, host):
		MnExec(host, CmdMemcachedClient["kill"])
	def run_iperf_server(self, host):
		MnExec(host, CmdIperfServer["start"])
	def stop_iperf_server(self, host):
		MnExec(host, CmdIperfServer["kill"])
	def run_iperf_client(self, host):
		MnExec(host, CmdIperfClient["start"].format(start_time = self.start_time, host_name = host, traffic_file = self.traffic_file))
	def stop_iperf_client(self, host):
		MnExec(host, CmdIperfClient["kill"])

def calc_score(a, b):
        scorea = 0
        scoreb = 0

        # mc_latency = map(float, filter(None, commands.getoutput("cat logs/*_mc.log").split('\n')))
        # latency_scores = map(lambda x: math.log(x, 10), mc_latency)
        # if len(latency_scores) > 0:
        #     scoreb = sum(latency_scores) / len(latency_scores)
        #     print "Average latency of Memcached Requests:", sum(mc_latency) / len(mc_latency), "(us)"
        #     print "Average log(latency) of Memcached Requests:", sum(latency_scores) / len(latency_scores)

        iperf_bps = map(float, filter(None, commands.getoutput("cat logs/*_iperf.log").split('\n')))
        bps_scores = map(lambda x: math.log(x, 10), iperf_bps)
        if len(bps_scores) > 0:
            scorea = sum(bps_scores) / len(bps_scores)
            print "Average throughput of Iperf Traffic:", sum(iperf_bps) / len(iperf_bps), "(bps)"
            print "Average log(throughput) of Iperf Traffic:", sum(bps_scores) / len(bps_scores)

        # print a * scorea - b * scoreb

def read_score_config(score_file):
        with open(score_file, "r") as file:
                a,b = map(float, file.readlines())
        return a,b

def make_log_dir():
        if os.path.exists('logs'): shutil.rmtree('logs')
        os.makedirs('logs')

def parse_hosts(host_string):
	host_list = []
	host_items = host_string.split(',')
	for host_item in host_items:
		if '-' in host_item:
			hosts = host_item.split('-')
			host_start = int(hosts[0])
			host_end = int(hosts[1])
			for i in range(host_start, host_end + 1):
				host_list.append("h%d" % i)
		else:
			host_list.append("h%d" % int(host_item))
	return host_list

if __name__ == '__main__':
	if len(sys.argv) != 4:
		print("usage: python evaluation.py <traffic file> <host list> <experiment time>")
		print("\ttraffic file: the trace file generated using the generate_trace.py.")
		print("\thost list: hosts involved in the trace file. If the hosts are h1, h2, h3, h5, h7, h8, you can type 1-3,5,7-8 here. No space allowed.")
		print("\texperiment time: how long do you want to send traffic using the trace.")
		exit()
	traffic_file = sys.argv[1]
	HOSTS = parse_hosts(sys.argv[2])
	duration = int(sys.argv[3])

	a = 1
	b = 1

	make_log_dir()

	e = Experiment(traffic_file, HOSTS, duration)
	e.start()
	calc_score(a, b)
