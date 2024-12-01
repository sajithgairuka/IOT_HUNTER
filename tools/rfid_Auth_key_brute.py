import RPi.GPIO as GPIO
import mylib.MFRC522 as MFRC522
import signal
import time
import argparse
import sys

def end_c_reader(signal, frame):
    global con_reader
    print("Ending the read.")
    con_reader = False
    GPIO.cleanup()
    sys.exit(0)


def read_keys_from_file(filename):
    keys = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    key = bytes.fromhex(line.replace(" ", ""))
                    if len(key) == 6:
                        keys.append(key)
        return keys
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return []

def parse_args(args):
    parser = argparse.ArgumentParser(prog='frame.py rfid_Auth_key_brute', 
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description='This script bruteforce the key in Mifare Classic card.',
                                 epilog="""Example usage:

            frame.py nfc_dump -k "rfid_auth_keys/keys.txt" """)
    
    parser.add_argument("-k","--keyfile",default="rfid_auth_keys/keys.txt",help="Path to the key file (e.g., rfid_auth_keys/keys.txt)")
    args = parser.parse_args(args)
    return args

def all_code(args):
    keys = read_keys_from_file(args.keyfile)
    signal.signal(signal.SIGINT, end_c_reader)
    c_reader = MFRC522.MFRC522()
    print("Press Ctrl-C to stop.")

    con_reader = True

    while con_reader:
        (status, TagType) = c_reader.MFRC522_Request(c_reader.PICC_REQIDL)

        if status == c_reader.MI_OK:
            print("Card detected")
            (status, uid) = c_reader.MFRC522_Anticoll()

            if status == c_reader.MI_OK:
                print("Card UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3]))

                c_reader.MFRC522_SelectTag(uid)

                key_found = False
                for key in keys:
                    print("Trying key:", key.hex())
                    status = c_reader.MFRC522_Auth(c_reader.PICC_AUTHENT1A, 8, key, uid)
                    if status == c_reader.MI_OK:
                        print("Key found:", key.hex())
                        key_found = True
                        break

                    time.sleep(0.1)

                if not key_found:
                    print("No valid key found.")

def module_main(args):
    args = parse_args(args)
    all_code(args)
