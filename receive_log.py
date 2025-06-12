from scapy.all import sniff, Raw, Packet, ShortField
from scapy.layers.inet import IP
from scapy.packet import bind_layers

class RIFO(Packet):
    name = "RIFO"
    fields_desc = [ShortField("rank", 0)]

bind_layers(IP, RIFO)

# Számláló beállítása
counter = 0

def handle(pkt):
    global counter
    
    if RIFO in pkt and pkt[IP].src != "10.0.1.2":
        counter += 1
        rank = pkt[RIFO].rank
        src = pkt[IP].src
        dst = pkt[IP].dst
        print(f"[{counter}] Received rank={rank} from {src} -> {dst}")

sniff(iface="h2-eth0", prn=handle)
