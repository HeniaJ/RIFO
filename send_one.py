from scapy.all import Ether, IP, sendp
from config import get_network_config, RIFO
from scapy.packet import bind_layers

bind_layers(IP, RIFO)
cfg = get_network_config()
test_rank = 10

pkt = Ether(dst=cfg["dst_mac"], src=cfg["src_mac"]) / \
      IP(dst=cfg["dst_ip"], src=cfg["src_ip"]) / \
      RIFO(rank=test_rank)

sendp(pkt, iface=cfg["iface"], verbose=False)
print(f"Packet sent with rank={test_rank} from {cfg['src_ip']} -> {cfg['dst_ip']} on {cfg['iface']}")