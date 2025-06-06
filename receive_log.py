from scapy.all import sniff, Raw, Packet, bind_layers
from scapy.fields import ShortField
from scapy.layers.inet import IP
from config import get_network_config

class RIFO(Packet):
    name = "RIFO"
    fields_desc = [ShortField("rank", 0)]

bind_layers(IP, RIFO)

def handle(pkt):
    if RIFO in pkt:
        print(f"Received packet with rank={pkt[RIFO].rank}")
    else:
        print("Received packet without RIFO header")

cfg = get_network_config()
sniff(iface=cfg["iface"], prn=handle)