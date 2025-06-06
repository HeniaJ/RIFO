from scapy.all import Ether, IP, sendp, Raw
from scapy.packet import Packet, bind_layers
from scapy.fields import ShortField
import time

class RIFO(Packet):
    name = "RIFO"
    fields_desc = [ShortField("rank", 0)]

bind_layers(IP, RIFO)

iface = "h1-eth0"
ranks = [10, 50, 100, 150, 200]

for r in ranks:
    pkt = Ether() / IP(dst="10.0.0.2") / RIFO(rank=r) / Raw(load=f"Test rank={r}")
    print(pkt.show())
    sendp(pkt, iface=iface, verbose=False)
    print(f"Sent packet with rank={r}")
    time.sleep(0.5)
