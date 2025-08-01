# port_scanner_module.py

import socket
import threading
from queue import Queue
import csv
import time # Make sure time is imported here if used in functions

# Global lock for console printing (still useful for debugging/status updates)
console_print_lock = threading.Lock()

# Define the CSV file name (can be overridden by the calling script if desired)
OUTPUT_CSV_FILE = "scan_results.csv"

def grab_banner(s):
    """
    Attempts to receive data (banner) from an open socket.
    Returns the decoded banner string or an empty string on failure.
    """
    try:
        s.settimeout(0.5) # Ensure a timeout for banner grabbing too
        banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
        banner = ' '.join(banner.split()) # Clean up excessive whitespace
        return banner
    except socket.timeout:
        return "[No banner received within timeout]"
    except Exception as e:
        return f"[Error grabbing banner: {e}]"

def scan_port_worker(host, port, timeout=1, results_q=None):
    """
    Attempts to connect to a specific port and grab its banner if open.
    Puts results into the results_q.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    
    try:
        result = s.connect_ex((host, port))
        if result == 0:
            banner_info = ""
            if port == 80: # Standard HTTP port
                s.send(b"GET / HTTP/1.1\r\nHost: " + host.encode() + b"\r\nConnection: close\r\n\r\n")
            
            banner_info = grab_banner(s)
            
            if results_q:
                # Put a dictionary for easier handling in CSV writer
                results_q.put({'Host': host, 'Port': port, 'Service_Banner': banner_info})
            
            with console_print_lock:
                print(f"[+] {host}:{port} is OPEN. Service: {banner_info[:70]}...") # Truncate for display
                
    except socket.error as e:
        pass 
    except Exception as e:
        with console_print_lock:
            print(f"An unexpected error occurred for {host}:{port}: {e}")
    finally:
        s.close()

def port_scanner_thread_worker(timeout, ports_to_scan_queue, results_q):
    """
    Worker function for each thread to pull (host, port) tuples from the queue and scan them.
    """
    while True:
        host_port_tuple = ports_to_scan_queue.get()
        if host_port_tuple is None: # Sentinel value
            break
        scan_port_worker(host_port_tuple[0], host_port_tuple[1], timeout, results_q) # Unpack tuple here
        ports_to_scan_queue.task_done()

def csv_writer_thread_worker(results_q, filename):
    """
    Dedicated thread worker to write results from the results_q to a CSV file.
    """
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Host', 'Port', 'Service_Banner']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader() # Write the header row
        
        while True:
            result = results_q.get()
            if result is None: # Sentinel value to signal exit
                break
            
            # result is already a dictionary from scan_port_worker
            writer.writerow(result)
            csvfile.flush() 
            results_q.task_done()
    
    with console_print_lock:
        print(f"\n[+] All scan results written to {filename}")

# Optional: Add a main function for the module itself for direct testing
if __name__ == "__main__":
    print("This is the port_scanner_module.py file.")
    print("It contains functions for port scanning and banner grabbing.")
    print("You can import these functions into another script to use them.")
    # Example of how you might test a single port directly for development
    # scan_port_worker("localhost", 80)