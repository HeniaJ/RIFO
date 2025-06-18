import threading
import queue
from scapy.all import sniff, Raw, Packet, ShortField
from scapy.layers.inet import IP
from scapy.packet import bind_layers
from config import get_network_config, RIFO

bind_layers(IP, RIFO)
cfg = get_network_config()

# szalbiztos tarolasa a csomagoknak
pkt_queue = queue.Queue()
counter = 0
lock = threading.Lock()

# csomagok feldolgozasa
def worker():
    global counter
    while True:
        pkt = pkt_queue.get()
        if pkt is None:
            break
        if RIFO in pkt and pkt[IP].src != cfg["src_ip"]:
            with lock:
                counter += 1
                rank = pkt[RIFO].rank
                src = pkt[IP].src
                dst = pkt[IP].dst
                print(f"[{counter}] Packet received with rank={rank} from {src} -> {dst} on {cfg['iface']}")
        pkt_queue.task_done()

# 15 szalon fut egyszerre a csomagfeldolgozas
for _ in range(15):
    threading.Thread(target=worker, daemon=True).start()

# beerkezo csomagok betoltese a queueba
def enqueue(pkt):
    pkt_queue.put(pkt)

# csomagkovetes
sniff(iface=cfg["iface"], prn=enqueue, store=0)
