from scapy.all import *

pkt = Ether(dst="00:00:00:00:00:02", src="00:00:00:00:00:01") / \
      IP(dst="10.0.0.2", src="10.0.0.1") / \
      Raw(load=b'\x00\x0a')  # RIFO rank = 10

sendp(pkt, iface="h1-eth0")