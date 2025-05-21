from scapy.all import sendp, Ether, IP, UDP, Raw
from time import sleep
import random

for i in range(100):
    rank = random.randint(0, 255)
    pkt = Ether() / IP(dst="10.0.0.2") / UDP(sport=1234, dport=4321) / Raw(load=bytes([rank]))
    sendp(pkt, iface="h1-eth0", verbose=False)
    print(f"[{i}] Sent packet with rank={rank}")
    sleep(0.05)
