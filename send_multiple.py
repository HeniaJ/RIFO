from scapy.all import Ether, IP, sendp, Raw
from scapy.packet import bind_layers
import time
from config import get_network_config, RIFO

bind_layers(IP, RIFO)
cfg = get_network_config()
iface = cfg["iface"]
ranks = [10, 11, 9, 15, 4]

for r in ranks:
      pkt = Ether(src=cfg["src_mac"], dst=cfg["dst_mac"]) / \
            IP(src=cfg["src_ip"], dst=cfg["dst_ip"]) / \
            RIFO(rank=r) / \
            Raw(load=f"Test rank={r}")

      sendp(pkt, iface=iface, verbose=False)
      print(f"Packet sent with rank={r} from {cfg['src_ip']} -> {cfg['dst_ip']} on {cfg['iface']}")
      time.sleep(0.5)