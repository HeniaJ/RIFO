from scapy.all import get_if_list
from scapy.packet import Packet
from scapy.fields import ShortField

def get_network_config():
    interfaces = get_if_list()

    if "h1-eth0" in interfaces:
        return {
            "iface": "h1-eth0",
            "src_mac": "00:00:0a:00:01:01",
            "dst_mac": "00:00:0a:00:01:02",
            "src_ip": "10.0.1.1",
            "dst_ip": "10.0.1.2"
        }
    elif "h2-eth0" in interfaces:
        return {
            "iface": "h2-eth0",
            "src_mac": "00:00:0a:00:01:02",
            "dst_mac": "00:00:0a:00:01:01",
            "src_ip": "10.0.1.2",
            "dst_ip": "10.0.1.1"
        }
    elif "h3-eth0" in interfaces:
        return {
            "iface": "h3-eth0",
            "src_mac": "00:00:0a:00:01:03",
            "dst_mac": "00:00:0a:00:01:02",
            "src_ip": "10.0.1.3",
            "dst_ip": "10.0.1.2"
        }
    elif "h4-eth0" in interfaces:
        return {
            "iface": "h4-eth0",
            "src_mac": "00:00:0a:00:01:04",
            "dst_mac": "00:00:0a:00:01:02",
            "src_ip": "10.0.1.4",
            "dst_ip": "10.0.1.2"
        }
    elif "h5-eth0" in interfaces:
        return {
            "iface": "h5-eth0",
            "src_mac": "00:00:0a:00:01:05",
            "dst_mac": "00:00:0a:00:01:02",
            "src_ip": "10.0.1.5",
            "dst_ip": "10.0.1.2"
        }
    else:
        raise RuntimeError("Unknown host")

class RIFO(Packet):
    name = "RIFO"
    fields_desc = [ShortField("rank", 0)]