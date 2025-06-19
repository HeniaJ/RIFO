from scapy.all import sniff, Raw, Packet, ShortField
from scapy.layers.inet import IP
from scapy.packet import bind_layers
from config import get_network_config, RIFO

# halozati forgalom figyelese

bind_layers(IP, RIFO)
cfg = get_network_config()
counter = 0

def handle(pkt):
    global counter

    # csomag infok kiirasa monitorozashoz
    if RIFO in pkt and pkt[IP].src != cfg["src_ip"]:
        counter += 1
        rank = pkt[RIFO].rank
        src = pkt[IP].src
        dst = pkt[IP].dst
        print(f"[{counter}] Packet received with rank={rank} from {src} -> {dst} on {cfg['iface']}")

# csomagfigyeles elinditasa
sniff(iface=cfg["iface"], prn=handle, store=0, timeout=100)
