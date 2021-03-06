# Project 4: Monitoring tools and Statistics Analysis

## Objectives

* Learn to use the monitoring tools and analyze monitoring data on Mininet and P4. These tools will be useful debugging tools for your future projects. 
* Run monitoring tools	
	- Getting latency from applications.
	<!-- - Getting flow size distribution through tcpdump. -->
	- Getting packet latencies from tcpdump.
	- Getting traffic rate information through tcpdump.
	- Getting queue length through P4 registers. 
	<!-- - Implement the counting bloom filter algorithm in P4. -->
* Analyze the monitoring data
	- Why do we get high tail latencies at times?

## Getting Started

To get started with this project, you need to copy the following files from project 3.

- `topology/p4app_fat.json`.
- `p4src/ecmp.p4`.
- `p4src/include/headers.p4`.
- `p4src/include/parsers.p4`.
- `controller/controller_fat_ecmp.p4`.

## Monitoring Tools

Sniffing traffic can be a very powerful tool when monitoring the traffic. 
There is a wide range of tools that can be used:

### Pcap Files:

By default, pcap option is enabled for the Mininet. 
When a packet arrives at an interface (port) at one switch, the switch will dump the packet into a pcap file.
After running the Mininet, you can see a list of pcap files in the directory `./pcap`.
Pcap logging will create several files using the following naming: `<sw_name>-<intf_num>_<in|out>.pcap`.

In a word, by reading those pcap files, you can learn how each packet is forwarded from the source to the destination.
Those pcap files are recorded in a specific binary format. You could use some pcap parser like `tcpdump` to read it.

**NOTE**: The name of pcap files have 'in' and 'out' to identify whether the packet goes into the switch or goes out of the switch. Please note that the pcap file with 'in' means the packet goes out of the switch, while the file with 'out' means the packet goes in the switch.

### Wireshark/Tshark:

Another option is to observe the traffic as it flows. For that you can use tools like `tshark` and its GUI version `wireshark`. Wireshark
is already installed in the VM, you can find its executable in the desktop.

To capture traffic with tshark run:

```bash
sudo tshark -i <interface_name>
```

### Tcpdump:

Similarly, and if you prefer, you can use `tcpdump` (also already installed in the VM).
To capture traffic with tcpdump run (shows link-layer information and does not resolve addresses):

```bash
sudo tcpdump -enn -i <interface_name> > <output file>
```

The output of tcpdump is in plain text. Like pcap files, the output of tcpdump also includes all packets arriving to the interface. Here is a brief introduction for the tcpdump item format:

For ICMP packet, the format is like this

```
19:35:11.688159 00:00:00:02:01:00 > 00:00:0a:00:00:02, ethertype IPv4 (0x0800), length 98: 10.0.0.11 > 10.0.0.2: ICMP echo request, id 3036, seq 1, length 64
```
Where the fields are *timestamp*, *source mac address > destination mac address*, *ethernet type*, *packet length*, *source IP address > destination IP address*, *ICMP packet type*, ...

For TCP packet, the format is like this

```
20:38:28.315819 00:00:00:02:01:00 > 00:00:0a:00:00:02, ethertype IPv4 (0x0800), length 9514: 10.0.0.3.34078 > 10.0.0.2.5002: Flags [.], seq 793632:803080, ack 1, win 56, options [nop,nop,TS val 1335200 ecr 1333906], length 9448
20:38:28.400434 00:00:00:02:01:00 > 00:00:0a:00:00:02, ethertype IPv4 (0x0800), length 66: 10.0.0.15.40798 > 10.0.0.2.5014: Flags [.], ack 2, win 56, options [nop,nop,TS val 1335242 ecr 1333990], length 0
```

Where the fields are *timestamp*, *source mac address > destination mac address*, *ethernet type*, *packet length*, *source IP address:TCP port > destination IP address:TCP port*, *TCP flags*, *sequence number/ack number*, ...

Other packets have similar formats.

<!-- ## Task 1: Implementing UDP and ICMP

First, you are going to support UDP and ICMP protocols in your ECMP implementation, since previously we only care about TCP packets.
Different from TCP, UDP does not have congestion control, so UDP packet senders could decide the sending rate themselves. Therefore, UDP traffic could cause congestion persistently.
ICMP is only used for error-reporting, which is used in `ping` and `traceroute` applications.

We provide you with headers of UDP protocol and ICMP protocol in `p4src/include/extra.p4`, and you need to copy those two headers in your P4 codes. **We are not going to grade your implementation on UDP and ICMP, but later tasks will require the processing logic of UDP and ICMP.** -->

## Task 1: Analyze the Latency of Applications

You are going to analyze the latency of Memcached applications in this task.

In this part, we focus on the latency of memcached requests and understand the latency changes when these requests coexist with incast flows. Please take the following steps. 

**Application trace**. We provide you with a trace named `apps/trace/mc.trace`, which runs memcached servers on `h2-h16`, and runs a memached client on `h1`. The client will send a memcached request every 0.1 second. After running the trace, the latency of each memcached request will be logged in `logs/h1_mc.log` file.

**Run:** Run the Mininet using the fattree topology `topology/p4app_fat.json` from the last project. Then run the ecmp controller `controller/controller_fat_ecmp.py`.
```
# Terminal 1
sudo p4run --conf topology/p4app_fat.json
```
```
# Terminal 2
python controller/controller_fat_ecmp.py
```
Next, send the incast flows using our bash script
```
sudo bash apps/run_incase.sh
```
After the messages are printed, then run the trace.
```
sudo python apps/send_traffic.py apps/trace/mc.trace 1-16 60
```
After running the trace, kill the incast flow sender.
```
sudo pkill tg
```

**Latency logs:** After running the trace, you can get latency from the `./logs` directory. You can find files looking like `h1_mc.log`, where each line represents the latency for one request.

### Questions

- Draw the CDF figure for all latencies of memcached requests. Name it `report/latency_cdf.pdf(png)`.
- What is the medium latency? What is the 99-th percentile tail latency for memcached respectively?
- Why do you think memcached has a long tail latency? Please use a single sentence to describe your reason.

**Note: We highly encourage you to write scripts for each step of your analysis and write scripts to generate figures. This will allow you to reuse these analysis for debugging your future projects. To make a clean directory structure, please put all your tool codes under the `./tools` directory.**

<!-- <mark>Delete?</mark>
## Task 2: Flow Size Distribution

In this part, you are expected to analyze the flow size distribution of Memcached and Iperf respectively. A flow is defined as a burst of packets sharing the same "five-tuple": source IP address, destination IP address, source TCP/UDP port number, destination TCP/UDP port number, and protocol (TCP or UDP). If two packets sharing the same five-tuple are separated by a sufficient time gap, then these two packets should belong to two different flows. 
Here we use a default value of 100ms as the time gap.

**Traces:** In order to check the flow size distribution for both Memcached and Iperf, we need to generate a trace that separate the traffic of those two applications. Please generate a trace file running Memcached on host `h1-h8`, and running Iperf on host `h9-h16`. The trace lasts for 60 seconds. Name it **trace2.txt**.

**Traffic data collection:** Use `tcpdump` to dump packet information. Note that you need to run `tcpdump` to collect traffic trace for each host. Think about on which interfaces it is required to run `tcpdump`. You can also use `tcpdump` to read pcap files.

**Analayze the tcpdump data:**
	You are supposed to write scripts that extract flow size information from the tcpdump traces. The packet information from `tcpdump` looks like
```
03:21:47.361011 00:00:0a:00:00:0a > ff:ff:ff:ff:ff:ff, ethertype ARP (0x0806), length 42: Request who-has 10.0.0.1 tell 10.0.0.10, length 28
03:21:47.361028 00:00:0a:00:00:01 > 00:00:0a:00:00:0a, ethertype ARP (0x0806), length 42: Reply 10.0.0.1 is-at 00:00:0a:00:00:01, length 28
03:21:47.370714 00:00:0a:00:00:0a > 00:00:0a:00:00:01, ethertype IPv4 (0x0800), length 74: 10.0.0.10.36128 > 10.0.0.1.5001: Flags [S], seq 2047321949, win 28380, options [mss 9460,sackOK,TS val 7033839 ecr 0,nop,wscale 9], length 0
...
```	
Each line represents a packet. For this analysis, you need to understand the first several fields of each line. The fields are: timestamp, source MAC address, destination MAC address, ethernet type, packet size, source IP address + source port number, destination IP address + destination port number. Note that the field `10.0.0.1.5001` means the IP address is `10.0.0.1`, and the port number is `5001`. You can use the MAC addresses to determine which flow the packet belongs to, and use the packet size to calculate the flow size distribution.

*Note*: For more references of `tcpdump`, please check the following website [Manpage of TCPDUMP](https://www.tcpdump.org/manpages/tcpdump.1.html) or [WizardZines](https://wizardzines.com/zines/tcpdump/)

### Questions

- Draw the CDF of flow size distribution for each application. Name it `report/mc_dist.pdf(png)` for memcached and `report/iperf_dict.pdf(png)` for iperf.
- For each application what is the average and medium? flow size respectively? And what is the average and medium flow completion time?
- What is the average and medium packet size of iperf and memcached flows respectively?
- How many flows are there in memcached and iperf applications respectively? 
- After gathering flows from iperf and memcached, what is the minimum percentage of flows that take up more than the 80\% traffic size? What can you conclude after getting the number? Please use a single sentence to describe your conclusion. -->

## Task 2: Queue Length

The key concept impacting the latency of memcached requests is the queue length. Each interface (port) of switches has a queue to buffer packets, in order to tolerate the sudden increase in the traffic rate. However, a long queue in a switch could significantly increase the latency of a packet. In this task, you are expected to read the longest queue length along the path of a packet, and add this information in an additional packet header.

### Probe Packets

We do not expect switches to add queue information to all packets, because it could not only increase the overhead of the switches, but also make those packets unrecognized by the hosts (since we add another packet header that should not exist). Therefore, we send a few "probe packets", that are sent and received by our probe applications, to detect the queue information.
We provide you with the probe sender and the probe receiver. The probe sender will send one packet periodically, and the probe packet will be processed by switches, and finally sent to the probe receiver. The probe receiver will get the longest queue length and write it to the log.

### Adding Telemetry Header

When the probe packet is sent to the first switch from the host, the switch should add a telemetry header to the packet. Here are what you need to do:

1. Create a header struct named `telemetry_t`, which contains 16-bit queue length, and 16-bit next header type.
2. Define ethernet type `TYPE_TELE` as `0x7777`, which is used to represent the telemetry header.
3. Modify the parser. If the telemetry header exists, the parser should parse ethernet header first, then the telemetry header, and then later headers including the IP header, the TCP header, *e.t.c.*
4. Modify the deparser.
5. In the egress pipeline, set telemetry header valid if 
	- The telemetryheader is invalid, and
	- The TCP port number is 7777.
Then record the largest queue length along the path. The queue length is stored in `standard_metadata.enq_qdepth`.

### Test Your Solution

1. Run your topology.
2. We provide you with a script `apps/run_probe.sh`, which will run a probe received on `h1`, and run one probe sender on `h2-h16`. The queue length will be stored in `report/qlen.txt`.
	```
	sudo bash apps/run_probe.sh
	```
3. Open another terminal, run the incast traffic
	```
	sudo bash apps/run_incast.sh
	```
4. After seeing the message, open another terminal, run the traffic trace
	```
	sudo python apps/send_traffic.py apps/trace/mc.trace 1-16 60
	```
5. After running the traffic, press `CTRL-C` to close probe receiver and probe sender, and run the following command to close the incast traffic generator.
	```
	sudo pkill tg
	```
6. Check `tools/qlen.txt` to get the queue lengths.

### Question

- Draw a figure to show the longest queue lengths. The x axis is the time, and the y axis is the longest queue length. Name the figure `report/qlen.pdf(png)`.
- Draw a figure to show the input traffic rate of the interface `t1-eth1` using the tcpdump results. The x axis is the time, and the y axis is the traffic rate (using `Mbps` as the unit). Measure the input traffic rate for every 0.1 second. Name the figure `report/rate.pdf(png)`. 
- Draw a figure to show the latency of memcached requests. The x axis is the time, and the y axis is the latency. Name it `report/mc_req.pdf(png)`.
- Use tcpdump to collect all the memcached packet latencies, and draw a figure to show the latency of all those memcached packets. The x axis is the time, and the y axis is the latency. Name it `report/mc_pkt.pdf(png)`. 
- Compare the figure of queue length and that of traffic rate, and answer the question: what is the correlation between the queue length and the traffic rate? Use a single sentence to describe it.
- Compare the figure of latency and queue length, and answer the question: what is the correlation between the queue length and the latency? Use a single sentence to describe it.

**Note**:
1. Be careful that the tcpdump will dump all input packets and output packets for that interface, but we only care about the input packets because we care about the input traffic rate.
2. Memcached server uses the port number `11211`, and thus packets with either source port number or destination port number `11211` belong to memcached packets.
3. Packet latency is not the request latency (flow latency).

<!-- ## Task 3: Queue Length Registers

Heavy hitters can significantly impact the network, causing long latencies of memcached requests. When every packet arrives at a switch, the queue length the packet sees is a significant metric for understanding the impact of heavy hitters and evaluating the congestion in the network. Here you are expected to implement P4 codes to read and store queue lengths, and read average queue lengths from a controller. 

### Implementing Registers for Queue Lengths

Since reading and dumping the queue length of each packet results in large overhead, you are going to record and dump the average queue length within a certain time range. Here are what you need to do:

1. Create a register array named `inport_qlen`, which has enough number of registers so that the it can record the queue length for each interface (port). In other words, `inport_qlen[i]` records the queue length information of the `i`-th interface.
2. Create another register array named `inport_packets`, which has the same width as `inport_qlen`. It records the number of packets arrived through each interface.
3. For each packet arrived at a certain interface, add the queue length to the corresponding register in `inport_qlen`. The queue length is stored in `standard_metadata.enq_qdepth`. Increase the corresponding register in `inport_packets` as well. 

### Reading Queue Length Periodically

We provide you with a controller file named `tools/read_stats.py`, which reads the queue length info of one switch. You can use the example to write your own codes. Please modify the file `tools/read_stats.py` to implement a register reader.

You should modify this file in the following way:
1. Read all registers periodically, per 0.1 second.
2. Get the delta of each register, so you can get the sum of queue lengths and the number of packets during the last 0.1 second for each interface.
3. Calculate the average queue length, and report the number to a file for each interface. The format of the data is: each line represents a period, and the format is `<timestamp> <average queue length>`. The format of the filename is `report/qlen/[sw_name]-[interface_name].txt`. For example, to monitor the average queue length for interface `eth1` on switch `t1`, the filename is `report/qlen/t1-eth1.txt`.

*Note*: For this experiment, we are using trace file **trace1.txt**. Since we only run applications on `h1-h8`, only switches in the first two pods and core switches should be involved. Therefore, you only need to calculate average queue lengths for interfaces on those switches.

### Experiment

**Trace**. Use trace file **trace1.txt**.

**Run**. First run `python tools/read_stats.py` to let it polls for the queue lengths. Then you can run the trace using `apps/send_traffic.py`. After running the trace, you can stop the `read_stats.py` script to get the numbers.

**Tcpdump**. Use tcpdump to monitor interface `t1-eth1`, and save the result to files. You can choose the name of those files, we are not going to grade on them. 

**Collect**. Use the `tools/read_stats.py` to collect queue length data in registers.

### Questions

- Draw figures to show the average queue lengths of the interface `t1-eth1`. The x axis is the time, and the y axis is the average queue length or the bandwidth during the period. Name the figure `report/qlen_eth1.pdf(png)`.
- Draw figures to show the input traffic rate of the interface `t1-eth1` using the tcpdump results. The x axis is the time, and the y axis is the traffic rate (using `Mbps` as the unit). Measure the input traffic rate for every 0.1 second. Name the figure `report/tr_eth1.pdf(png)`. **Be careful that the tcpdump will dump all input packets and output packets for that interface, but we only care about the input packets because we care about the input traffic rate**.
- Compare the figure of queue length and that of traffic rate, and answer the question: what is the correlation between the queue length and the traffic rate? Use a single sentence to describe it.
- Draw figures to show the latency of memcached on `h1`. The x axis is the time, and the y axis is the latency. Name it `report/lat_h1.pdf(png)`.
- Compare the figure of latency and queue length, and answer the question: what is the correlation between the queue length and the latency? Use a single sentence to describe it.

### Note

The queue length should be 0 for most of the time, and there could be some spikes on the queue lengths, but the highest average queue length could be as low as 2. It is totally fine if you always get a low number, as long as the number in spikes is larger than 0. -->

<!-- ## Task 5: Heavy Hitter Detection

The above analysis is offline: collecting data first and analyze it later. Here, we will explore how to capture useful information online with a p4 program. 
Your job here is to write a heavy hitter detector to run at the switches. 

**Heavy hitter definition:** Assume that the total amount of traffic size is *x*, and given a threshold *t*, heavy hitters are defined as those flows whose size is larger than *tx*. In this project, we set the threshold t as 0.05.

**Implementing heavy hitter detection algorithm on P4:**
A naive solution to detect heavy hitters is to use a list.
However, using a list to record all flows consume too much memory that switches cannot support it, and it also requires switches to navigate the list for every packet.
Therefore, we choose to use the Counting Bloom Filter (CBF) solution, which is more time-efficient and memory-efficient. CBF is basically a hash table with fixed number of buckets, which allows hash collision.
You can check the [CBF wiki page](https://en.wikipedia.org/wiki/Bloom_filter#Counting_filters) for more references.

The CBF algorithm is as follows.
1. Define an array of registers with `w` register. Here you are going to run 3 cases, where `w` is equal to 128, 512, and 1024. The initial value of each register is 0.
2. For each incoming packet, use two independent hash functions to calculate two hash values for the packet "five-tuple" (src ip, dst ip, src port, dst port, protocol). Use module operation to guarantee that the two hash values are between 0 and `w-1`.
3. Assume that the two hash values are *x1* and *x2*, and the packet size is *s*. Then add *s* to two registers whose index is *x1* and *x2*.
4. After running your traffic, read the register array. For each flow, use its two hash values to locate the two registers, and the one with smaller value is the estimated flow size. 

*Note*:
1. **Define P4 registers**. A register array is defined in the following way: `register<bit<BIT_WIDTH>>(NUM_OF_REGISTERS) register_name`.
2. **P4 register operations**. Registers has `read` and `write` operations. The signature of the `read` and `write` is: `register_name.read/write(<output/input field>, <index>)`.
3. **Hash functions**. P4 provides several hash functions to use. Here we recommend using `crc16` and `crc32` hash functions. The signature of a hash function is: 
`hash(<output_field>, <HashAlgorithm.crc16 or crc32>, (bit<1>)0, {<field1 to hash>, <field2 to hash>, ...}, (bit<16>)4096)`.

**Trace:** Use trace **trace1.txt**. 

**Run**: Run the trace with `apps/send_traffic.py`.

**Tcpdump**: Use tcpdump to collect packets on each host.

**Read the counters**. Write another Python script named `tools/read_hh.py`, which reads the all CBF registers after running the traffic. You only need to check the registers on **ToR switches**, and be aware that each packet goes through only one or two core switch. 

**Collect heavy hitters**. You can use the tcpdump result to get all flows within the traffic, and use the CBF algorithm to read the estimated flow size of the flow. Then you can calculate the list of heavy hitters. If you are confused how to implement the same hash function in Python, please refer to this website [https://github.com/p4lang/tutorials/issues/188].

### Notes

If you are using crc16 and crc32 in your p4 code, then you can create the two hash functions as follows:
```
crc16 = crcmod.predefined.mkCrcFun('crc-16')
crc32 = crcmod.predefined.mkCrcFun('crc-32')
```
Then you need to collect the 5-tuple for each flow. You need to first convert each field into integers
```
IP address: 10.0.0.1 -> 0x0a000001
```
Port numbers and protocol are integers so there is no need to convert.
Second, you need to convert each integer into byte string with big-endien using the following function.
```
def int_to_bytes(value, length):
    result = []

    for i in range(0, length):
        result.append(value >> (i * 8) & 0xff)

    result.reverse()

    return bytes(bytearray(result))
```
Finally you need to combine the five fields together (sip, dip, sport, sport, protocol) into a 13-byte byte string, and then you can use the two hash functions to calculate the hash value
```
idx1 = crc16(s) # s is the string
idx2 = crc32(s)
```

### Questions

- Report heavy hitters and their flow sizes (five tuple + flow size) in `report/hh.txt` for the three cases. How many flows are there in the heavy hitters?
- Check the accuracy of the heavy hitters by getting the real flow sizes from tcpdump results, and compare the accuracy with different `w`.
<!-- - Within the core switch `c1`, what are the heavy hitters and their corresponding flow sizes? Which application are those heavy hitters from?
- Within the core switch `c2`, what are the heavy hitters and their corresponding flow sizes? Are they the same with those within `c1`? Based on the result, does the ecmp solution make the traffic fully balanced?
- Within the aggregate switch `a1`, what are the heavy hitters? Are they the same with those within `c1`?
- Within the ToR switch `t1`, what are the heavy hitters? Which host are those heavy hitters from? -->


## Task 3: Analyze the Congestion

In previous part, you can learn there are long tail latencies for some memcached requests. Those long tail latencies come from congestions in the network, which means there is a long queue in some switches, introducing a long queuing delay for memcached request packets.

In this part, you need to analyze why there is a congestion in the network. 

**Pick up a problem**. After running the traffic, you can use tcpdump to get the flow latency of all memcached flows. Pick a memcached flow with 99-percentile tail latency. Record the time when the packets of the flow are sent in the network.

**Check routing path**. Using tcpdump reports, you can learn how those packets are routed within the network. Record the path. 

**Analyze the long latency**. You need to use the information from the pcap files, the queue length, the probe packets, to analyze why the flow experience a long latency.

<!-- You can get average queue length information after reading counters from P4 switches, and you can use the information to detect congestion.  -->
<!-- After detecting a congestion, you can use packet information from `tcpdump` to find out why there is a congestion.<mark>How do I correlate the two traces? Just based on timestamp?</mark> -->

<!-- <mark> Since we already get queue length data, it seems here we just need to ask few more questions about long tail latency by asking students to investigate the other data they collected. Or maybe we can change the order: latency, flow size, bw counter, queue counter???</mark> -->
<!-- ### Detailed Steps

- Generate application traces. You need to generate Memcached traces on host h1 and h4, and generate iperf traces on host h1-h8, for 60 seconds.
- Run the Fattree topology.
- Use ``tcpdump`` to dump packet information.
- Run ``read_counters.py`` script.
- Run ``send_traffic.py`` script.
- After finishing the experiments, find the top-5 queue lengths across the whole experiments.
- Use the ``tcpdump`` information to describe why there is a long queue for the top-5 queue lengths. -->

### Questions

<!-- - When memcached requests suffer from long latencies, what is happening in the network? <mark>This question is too vauge. Ask more specific questions</mark> -->
- For the memcached flow you pick up, what is the routing path for it?
- Why the flow experiences a long latency?

## Submission and Grading

### What to Submit

<!-- - The heavy hitter detection and queue length register implementation in `p4src/ecmp.p4` in `ecmp` topology directory. -->
- All the plotted figures. It requires you to plot those figures on your own. Please put all figures in `report` directory. 
- The telemetry header implementation in `p4src/ecmp.p4`.
<!-- - Two register readers `tools/read_stats.py` and `tools/read_hh.py`. -->
- Answer the questions in the file `report/report.txt`. Please also include the meaning for each figure you draw in this file. (We can hardly understand the figure by only looking at the file name.)

### Grading

- *40*: the implementation of the telemetry header.
- *20*: plotted figures.
- *40*: answer the questions.

### Survey

Please fill up the survey when you finish your project.

[Survey link](https://docs.google.com/forms/d/e/1FAIpQLSfhpJxb82bjq0Tyyx1AZ1O_OiGdGyEwzguebrkVI4bMJGOoYA/viewform?usp=sf_link)
