from scapy.all import sniff, Raw, Packet, ShortField
from scapy.layers.inet import IP
from scapy.packet import bind_layers

class RIFO(Packet):
    name = "RIFO"
    fields_desc = [ShortField("rank", 0)]

bind_layers(IP, RIFO)

def handle(pkt):
    if RIFO in pkt:
        print(f"Received RIFO rank = {pkt[RIFO].rank}")
    else:
        print("Packet has no rank field")

sniff(iface="h2-eth0", prn=handle)
