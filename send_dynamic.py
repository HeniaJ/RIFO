from scapy.all import sendp, Ether, IP, Raw
from scapy.packet import bind_layers
from time import sleep
import random
from config import get_network_config, RIFO

bind_layers(IP, RIFO)
cfg = get_network_config()

for i in range(2000):
      rank = random.randint(0, 65000)
      pkt = Ether(src=cfg["src_mac"], dst=cfg["dst_mac"]) / \
            IP(src=cfg["src_ip"], dst=cfg["dst_ip"]) / \
            RIFO(rank=rank) / \
            Raw(load=f"Random rank={rank}")

      sendp(pkt, iface=cfg["iface"], verbose=False)
      print(f"[{i}] Packet sent with rank={rank} from {cfg['src_ip']} -> {cfg['dst_ip']} on {cfg['iface']}")
      #sleep(0.05)