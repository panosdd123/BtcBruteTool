
# ============= INSTAL ================
# pip install --upgrade cryptofuzz colorthon blessed xTerm
# =====================================
import os
import sys
import time
from cryptofuzz import Convertor, Generator
from colorthon import Colors as Fore
from blessed import Terminal
import concurrent.futures as cf
from xTerm import Table


conv = Convertor()
gen = Generator()
term = Terminal()
z = 0
w = 0
richAddress = set()
RICH_FILE = "Bits.txt"
FOUND_FILE = "found.txt"
MNEMONIC_SIZE = 12  # Can be set to 24 if needed


def get_time():
    """Get the current time formatted."""
    tt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return f"[{Fore.GREY}{tt}{Fore.RESET}] "


def get_title(message_text: str):
    """Set the terminal title."""
    sys.stdout.write(f"\x1b]2;{message_text}\x07")
    sys.stdout.flush()


def get_address_pairs(mnemonic_str: str):
    """Get compressed and uncompressed addresses from a mnemonic string."""
    caddr = conv.mne_to_addr(mnemonic_str, True)
    uaddr = conv.mne_to_addr(mnemonic_str, False)
    return caddr, uaddr


def data_export():
    """Generate and export data."""
    mnemonic = gen.generate_mnemonic(MNEMONIC_SIZE)
    compressed_addr, uncompressed_addr = get_address_pairs(mnemonic)
    return compressed_addr, uncompressed_addr, mnemonic


def handle_data(data, richAddress):
    global z, w
    z += 1
    """Handle the processing and logging of data."""
    compressed_addr, uncompressed_addr, mnemonic = data

    if compressed_addr in richAddress:
        w += 1
        log_data(f"Address: {compressed_addr}\nMnemonic: {mnemonic}\n")

    elif uncompressed_addr in richAddress:
        w += 1
        log_data(f"Address: {uncompressed_addr}\nMnemonic: {mnemonic}\n")


    # -- Output --
    track_prefix = f"{get_time()}[ Generate:{Fore.RED}{z}{Fore.RESET} Found:{Fore.GREEN}{w}{Fore.RESET} ] "
    track_suffix = f"{Fore.GREEN}{compressed_addr}{Fore.RESET}"
    termWidth = term.width
    sp = " " * (termWidth - (len(track_prefix) + len(track_suffix)) - 20)
    print(
        track_prefix, track_suffix, sp, f"{Fore.YELLOW}{uncompressed_addr}{Fore.RESET}"
    )
    print(f"{track_prefix}{Fore.GREY}{mnemonic}{Fore.RESET}")
    get_title(f"Total: {z} | Found: {w}")


def read_addresses_from_file(file_path=RICH_FILE):
    """Read addresses from a file."""
    with open(file_path, "r") as file:
        return set(line.strip() for line in file.readlines())


def log_data(log_string, file_path=FOUND_FILE):
    """Log data to a file."""
    with open(file_path, "a") as file:
        file.write(f"{log_string}\n")


def worker_thread():
    """Set up the Pool Processes and handle the data."""
    coreTotal = 4
    print(f"Core Total: {coreTotal}")
    print(f"Read File: {RICH_FILE}")
    richAddresses = read_addresses_from_file()
    print(f"Found File: {FOUND_FILE}")
    print(f"Total Import Address : {len(richAddresses)}")

    with cf.ProcessPoolExecutor(max_workers=coreTotal) as executor:
        while True:
            futures = {executor.submit(data_export): i for i in range(coreTotal)}
            for future in cf.as_completed(futures):
                try:
                    data = future.result()
                    handle_data(data, richAddresses)
                except Exception as exc:
                    print(exc)


if __name__ == "__main__":
    try:
        worker_thread()
    except KeyboardInterrupt:
        print("Process interrupted by user. ... Exiting ...")
        exit()
