class IperfTrace:
	def __init__(self, time, dst_ip, duration):
		self.time, self.dst_ip, self.duration = time, dst_ip, duration
	def __str__(self):
		return "%f 2 %s %f"%(self.time, self.dst_ip, self.duration)
