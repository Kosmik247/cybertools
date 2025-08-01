import socket
import threading
from queue import Queue
import time
import csv 


console_print_lock = threading.Lock()


OUTPUT_CSV_FILE = "scan_results.csv"

def grab_banner(s):
    try:
        banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
        banner = ' '.join(banner.split()) 
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
            banner_info = grab_banner(s)
            if results_q:
                results_q.put((host, port, banner_info))
            
            with console_print_lock: # Only allows one thread to print at a time
                print(f"[+] Port {port} is OPEN. Service: {banner_info[:70]}...") 
                
    except socket.error as e:
        with console_print_lock:
            print(f"[-] Error scanning port {port}: {e}")
        pass 
    except Exception as e:
        with console_print_lock:
            print(f"An unexpected error occurred for port {port}: {e}")
    finally:
        s.close()

def port_scanner_thread_worker(host, timeout, ports_q, results_q):
    """
    Worker function for each thread to pull ports from the ports_q and scan them.
    """
    while True:
        port = ports_q.get()
        if port is None: 
            break
        scan_port_worker(host, port, timeout, results_q)
        ports_q.task_done()

def csv_writer_thread_worker(results_q, filename):
    """
    Dedicated thread worker to write results from the results_q to a CSV file.
    """
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Host', 'Port', 'Service_Banner']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader() 
        
        while True:
            result = results_q.get()
            if result is None: 
                break
            
            host, port, banner = result
            writer.writerow({
                'Host': host, 
                'Port': port, 
                'Service_Banner': banner
            })
            csvfile.flush() # Forces data to be written immediately instead of being held in buffer as IO slow
            results_q.task_done()
    
    with console_print_lock:
        print(f"\n[+] All scan results written to {filename}")


if __name__ == "__main__":
    print("--- Accelerated Port Scanner with Banner Grabbing and CSV Output ---")
    
    target_host = input("Enter the target IP address or hostname: ") or "localhost"
    
    try:
        start_port = int(input("Enter the starting port number: "))
        end_port = int(input("Enter the ending port number: "))
    except ValueError:
        print("Invalid port number. Please enter integers.")
        exit()

    num_scanner_threads = int(input("Enter the number of scanner threads (e.g., 50, 100): "))
    scan_timeout = float(input("Enter connection timeout in seconds (e.g., 0.5, 0.1): "))

    print(f"\nScanning {target_host} from port {start_port} to {end_port} with {num_scanner_threads} threads...")
    
    ports_queue = Queue()  
    results_queue = Queue() 

    
    for port in range(start_port, end_port + 1):
        ports_queue.put(port)

    scanner_threads = []
    start_time = time.time()

    # Create and start scanner worker threads
    for _ in range(num_scanner_threads):
        t = threading.Thread(target=port_scanner_thread_worker, 
                             args=(target_host, scan_timeout, ports_queue, results_queue))
        t.daemon = True # Allows the main program to exit even if threads are still running
        t.start()
        scanner_threads.append(t)

    
    writer_thread = threading.Thread(target=csv_writer_thread_worker, args=(results_queue, OUTPUT_CSV_FILE))
    writer_thread.daemon = True # Can be daemon, main will wait for it via results_queue.join()
    writer_thread.start()

    # Wait for all port scanning tasks to complete
    ports_queue.join() 

    # Signal scanner threads to exit
    for _ in range(num_scanner_threads):
        ports_queue.put(None) 
    for t in scanner_threads:
        t.join() # Wait for scanner threads to finish

    # Signal the writer thread to exit (after all scan results have been put into results_queue)
    results_queue.put(None)
    writer_thread.join() # Wait for the writer thread to finish its work

    end_time = time.time()
    print(f"\nScan complete in {end_time - start_time:.2f} seconds.")
    print(f"Results saved to {OUTPUT_CSV_FILE}")