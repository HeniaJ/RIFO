from scapy.all import get_if_list
from scapy.packet import Packet
from scapy.fields import ShortField

def get_network_config():
    interfaces = get_if_list()

    host_configs = {
        f"h{i}-eth0": {
            "iface": f"h{i}-eth0",
            "src_mac": f"00:00:0a:00:01:{i:02d}",
            "dst_mac": "00:00:0a:00:01:01" if i != 1 else "00:00:0a:00:01:02",
            "src_ip": f"10.0.1.{i}",
            "dst_ip": "10.0.1.1" if i != 1 else "10.0.1.2"
        } for i in range(1, 16)
    }

    for iface in interfaces:
        if iface in host_configs:
            return host_configs[iface]

    raise RuntimeError("Unknown host")

class RIFO(Packet):
    name = "RIFO"
    fields_desc = [ShortField("rank", 0)]