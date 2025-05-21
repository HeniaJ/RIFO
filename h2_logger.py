from scapy.all import sniff, Raw

def handle(pkt):
    if Raw in pkt:
        rank = pkt[Raw].load[0]
        print(f"Received packet with rank={rank}")

sniff(iface="h2-eth0", prn=handle)
