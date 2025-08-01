import socket

def scan_port(host, port):
    """
    Attempts to connect to a specific port on a given host.
    Returns True if the port is open, False otherwise.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.1)
        result = s.connect_ex((host, port)) 
        if result == 0:
            return True
        else:
            return False
    except socket.error as e:
        print(f"Error scanning port {port}: {e}")
        return False
    finally:
        s.close() 

if __name__ == "__main__":
    target_ip = input("Enter the target IP address or hostname: ") or "localhost"

    try:
        start_p = int(input("Enter the starting port number: "))
        end_p = int(input("Enter the ending port number: "))
    except ValueError:
        print("Invalid port number. Please enter integers.")
        exit()

    print(f"\nScanning {target_ip} from port {start_p} to {end_p} on {target_ip}...")

    open_ports = []
    for port in range(start_p, end_p + 1):
        if scan_port(target_ip, port):
            print(f"[+] Port {port} is OPEN")
            open_ports.append(port)
        else:
            print(f"[-] Port {port} is closed/filtered")

    if open_ports:
        print(f"\nScan complete. Open ports found on {target_ip}: {open_ports}")
    else:
        print(f"\nNo open ports found on {target_ip} in the specified range.")