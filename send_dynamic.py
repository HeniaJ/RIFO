from scapy.all import sendp, Ether, IP, Raw
from scapy.packet import bind_layers
from time import sleep
import random
from config import get_network_config, RIFO

bind_layers(IP, RIFO)
cfg = get_network_config()

for i in range(100):
    rank = random.randint(0, 255)
    pkt = Ether(src=cfg["src_mac"], dst=cfg["dst_mac"]) / \
          IP(src=cfg["src_ip"], dst=cfg["dst_ip"]) / \
          RIFO(rank=rank) / \
          Raw(load=f"Random rank={rank}")

    sendp(pkt, iface=cfg["iface"], verbose=False)
    print(f"[{i}] Sent packet with rank={rank}")
    sleep(0.05)