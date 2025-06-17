from scapy.all import sniff, Raw, Packet, ShortField
from scapy.layers.inet import IP
from scapy.packet import bind_layers
from config import get_network_config

class RIFO(Packet):
    name = "RIFO"
    fields_desc = [ShortField("rank", 0)]

bind_layers(IP, RIFO)
cfg = get_network_config()
counter = 0

def handle(pkt):
    global counter
    
    if RIFO in pkt and pkt[IP].src != cfg["src_ip"]:
        counter += 1
        rank = pkt[RIFO].rank
        src = pkt[IP].src
        dst = pkt[IP].dst
        print(f"[{counter}] Packet received with rank={rank} from {src} -> {dst} on {cfg['iface']}")

sniff(iface=cfg["iface"], prn=handle)