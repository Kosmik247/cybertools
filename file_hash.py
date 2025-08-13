import hashlib
import os

BUF_SIZE = 65536  # Read file in 64KB chunks

def calculate_file_hash(filepath, hash_algo="sha256"):
    """
    Calculates the hash of a file using the specified algorithm.
    Returns the hexadecimal digest of the hash, or None if the file is not found.
    """
    if hash_algo == "md5":
        hasher = hashlib.md5()
    elif hash_algo == "sha256":
        hasher = hashlib.sha256()
    else:
        print("Unsupported hash algorithm. Using SHA256 by default.")
        hasher = hashlib.sha256()

    try:
        with open(filepath, 'rb') as f:  # Open in binary read mode
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break  # End of file
                hasher.update(data)
        return hasher.hexdigest()
    except FileNotFoundError:
        print(f"Error: File not found at '{filepath}'")
        return None
    except Exception as e:
        print(f"An error occurred while hashing the file: {e}")
        return None

if __name__ == "__main__":
    print("--- File Integrity Checker ---")
    
    # 1. First run: Calculate and store the initial hash (simulate)
    print("\n--- Initial Hashing ---")
    file_to_check = input("Enter the path to the file you want to monitor (e.g., my_document.txt): ")
    
    initial_hash = calculate_file_hash(file_to_check, "sha256") # You can change to "md5"
    
    if initial_hash:
        print(f"Initial SHA256 Hash of '{file_to_check}': {initial_hash}")
        # In a real scenario, would save this hash to a trusted location (e.g., a separate file, database).
        

        input("\n(Optional) Now, try modifying the file (e.g., open it and add a space, then save). Press Enter to continue and verify...")

        # 2. Second run: Calculate the hash again and compare
        print("\n--- Verifying Integrity ---")
        current_hash = calculate_file_hash(file_to_check, "sha256")

        if current_hash:
            print(f"Current SHA256 Hash of '{file_to_check}': {current_hash}")

            if initial_hash == current_hash:
                print("\n[+] File integrity VERIFIED: The file has NOT been modified.")
            else:
                print("\n[!] ALERT: File integrity COMPROMISED! The file HAS been modified.")
        else:
            print("Could not calculate current hash for comparison.")
    else:
        print("Exiting.")
