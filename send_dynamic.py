from scapy.all import sendp, Ether, IP, Raw
from scapy.packet import bind_layers
from time import sleep
import random
from config import get_network_config, RIFO

# ip fejlec utan a rifo (rang) kovetkezik
bind_layers(IP, RIFO)

# halozati konfig betoltese
cfg = get_network_config()

for i in range(100):
      # csomag rangjanak random generalasa
      rank = random.randint(0, 65000)

      # csomag keszitese
      pkt = Ether(src=cfg["src_mac"], dst=cfg["dst_mac"]) / \
            IP(src=cfg["src_ip"], dst=cfg["dst_ip"]) / \
            RIFO(rank=rank) / \
            Raw(load=f"Random rank={rank}")

      # csomag kuldese
      sendp(pkt, iface=cfg["iface"], verbose=False)
      print(f"[{i}] Packet sent with rank={rank} from {cfg['src_ip']} -> {cfg['dst_ip']} on {cfg['iface']}")
      sleep(0.5)
