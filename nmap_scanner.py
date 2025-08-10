import nmap
import netifaces
import ipaddress
import sys

def get_local_subnet():
    try:
        default_iface = netifaces.gateways()['default'][netifaces.AF_INET][1]
        ip_info = netifaces.ifaddresses(default_iface)[netifaces.AF_INET][0]
        ip_addr = ip_info['addr']
        netmask = ip_info['netmask']
        network = ipaddress.IPv4Network(f"{ip_addr}/{netmask}", strict=False)
        return str(network)
    except Exception as e:
        print("Could not determine local subnet:", e)
        sys.exit(1)

def run_scan(target, arguments):
    scanner = nmap.PortScanner()
    print(f"\nRunning scan on {target} with arguments: {arguments}")
    try:
        scanner.scan(hosts=target, arguments=arguments)
    except Exception as e:
        print("Scan failed:", e)
        return
    for host in scanner.all_hosts():
        print(f"\nHost: {host} ({scanner[host].hostname()})")
        print("State:", scanner[host].state())
        for proto in scanner[host].all_protocols():
            print(f"Protocol: {proto}")
            ports = scanner[host][proto].keys()
            for port in sorted(ports):
                print(f"Port: {port} — State: {scanner[host][proto][port]['state']}")

def print_menu():
    print("\n=== Nmap Scanner Menu ===")
    print("1. Fast scan (top 100 ports) on local network")
    print("2. Full port scan (all 65535 ports) on local network")
    print("3. Service/version detection on local network")
    print("4. OS detection & aggressive scan (slow)")
    print("5. Scan specific IP address")
    print("6. Exit")

def main():
    subnet = get_local_subnet()
    while True:
        print_menu()
        choice = input("Select an option (1–6): ").strip()
        if choice == "1":
            run_scan(subnet, "-T4 -F")
        elif choice == "2":
            run_scan(subnet, "-T4 -p-")
        elif choice == "3":
            run_scan(subnet, "-T4 -sV")
        elif choice == "4":
            run_scan(subnet, "-T4 -A")
        elif choice == "5":
            ip = input("Enter the IP address to scan: ").strip()
            run_scan(ip, "-T4 -sV")
        elif choice == "6":
            print("Exiting.")
            break
        else:
            print("Invalid selection. Please try again.")

if __name__ == "__main__":
    main()
