import threading
from queue import Queue
import time
import ipaddress
from scapy.all import ARP, Ether, srp


def get_ip_range_from_cidr(cidr):
    
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        # Exclude network address and broadcast address for typical host scanning
        return [str(ip) for ip in network.hosts()]
    except ValueError as e:
        print(f"Error parsing CIDR: {e}. Please use a valid CIDR (e.g., 192.168.1.0/24).")
        return []


if __name__ == "__main__":
    network = "192.168.0.1/24"  # Local network
    
    active_hosts_to_scan = get_ip_range_from_cidr(network)
    print(active_hosts_to_scan)