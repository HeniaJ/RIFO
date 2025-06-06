from scapy.all import sniff, Raw, Packet, bind_layers
from scapy.fields import ShortField
from scapy.layers.inet import IP, Ether

class RIFO(Packet):
    name = "RIFO"
    fields_desc = [ShortField("rank", 0)]

bind_layers(IP, RIFO)

def handle(pkt):
    print(pkt.show())
    if RIFO in pkt:
        print(f"Received packet with rank={pkt[RIFO].rank}")
    else:
        print("Received packet without RIFO header")

sniff(iface="h2-eth0", prn=handle)


'''
from scapy.all import sniff, Raw

def handle(pkt):
    if Raw in pkt:
        rank = pkt[Raw].load[0]
        print(f"Received packet with rank={rank}")

sniff(iface="h2-eth0", prn=handle)
'''