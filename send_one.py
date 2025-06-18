from scapy.all import Ether, IP, sendp
from config import get_network_config, RIFO
from scapy.packet import bind_layers

# csomag fejlecben ip utan a rang kovetkezik
bind_layers(IP, RIFO)

# halozati konfiguracio betoltese
cfg = get_network_config()

# teszt csomag rangjanak fix ertek beallitasa
test_rank = 10

# egy teszt csomag osszeallitasa
pkt = Ether(dst=cfg["dst_mac"], src=cfg["src_mac"]) / \
      IP(dst=cfg["dst_ip"], src=cfg["src_ip"]) / \
      RIFO(rank=test_rank)

# teszt csomag elkuldese es visszajelzes konzolon
sendp(pkt, iface=cfg["iface"], verbose=False)
print(f"Packet sent with rank={test_rank} from {cfg['src_ip']} -> {cfg['dst_ip']} on {cfg['iface']}")
