# main_app.py

import threading
from queue import Queue
import time
import ipaddress # A useful module for handling IP addresses and networks

# Import the functions from your port_scanner_module
from threaded_port_scanner import (
    port_scanner_thread_worker,
    csv_writer_thread_worker,
    OUTPUT_CSV_FILE, # You can import this or define it here
    console_print_lock # For consistent console output
)

def get_ip_range_from_cidr(cidr):
    """
    Generates a list of IP addresses from a CIDR notation (e.g., '192.168.1.0/24').
    """
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        # Exclude network address and broadcast address for typical host scanning
        return [str(ip) for ip in network.hosts()]
    except ValueError as e:
        print(f"Error parsing CIDR: {e}. Please use a valid CIDR (e.g., 192.168.1.0/24).")
        return []

if __name__ == "__main__":
    with console_print_lock:
        print("--- Network Scanner Application ---")
    
    # --- Input for Network Range ---
    # Using CIDR for more flexible network input
    network_cidr = input("Enter the target network in CIDR notation (e.g., 192.168.1.0/24): ")
    
    active_hosts_to_scan = get_ip_range_from_cidr(network_cidr)

    if not active_hosts_to_scan:
        exit()

    try:
        start_port = int(input("Enter the starting port number: "))
        end_port = int(input("Enter the ending port number: "))
    except ValueError:
        with console_print_lock:
            print("Invalid port number. Please enter integers.")
        exit()

    num_scanner_threads = int(input("Enter the number of scanner threads (e.g., 50, 100): "))
    scan_timeout = float(input("Enter connection timeout in seconds (e.g., 0.5, 0.1): "))

    with console_print_lock:
        print(f"\nDiscovered {len(active_hosts_to_scan)} hosts in {network_cidr}.")
        print(f"Scanning {len(active_hosts_to_scan)} hosts from port {start_port} to {end_port} with {num_scanner_threads} threads...")
    
    ports_to_scan_queue = Queue()   # Queue for (host, port) tuples to scan
    results_queue = Queue()         # Queue for storing scan results

    # Populate the ports queue with (host, port) tuples
    for host in active_hosts_to_scan:
        for port in range(start_port, end_port + 1):
            ports_to_scan_queue.put((host, port))

    scanner_threads = []
    start_time = time.time()

    # Create and start scanner worker threads
    for _ in range(num_scanner_threads):
        t = threading.Thread(target=port_scanner_thread_worker, 
                             args=(scan_timeout, ports_to_scan_queue, results_queue))
        t.daemon = True 
        t.start()
        scanner_threads.append(t)

    # Start the single CSV writer thread
    writer_thread = threading.Thread(target=csv_writer_thread_worker, args=(results_queue, OUTPUT_CSV_FILE))
    writer_thread.daemon = True 
    writer_thread.start()

    # Wait for all port scanning tasks to complete
    ports_to_scan_queue.join() 

    # Signal scanner threads to exit
    for _ in range(num_scanner_threads):
        ports_to_scan_queue.put(None) 
    for t in scanner_threads:
        t.join() 

    # Signal the writer thread to exit
    results_queue.put(None)
    writer_thread.join()

    end_time = time.time()
    with console_print_lock:
        print(f"\nScan complete in {end_time - start_time:.2f} seconds.")
        print(f"Results saved to {OUTPUT_CSV_FILE}")