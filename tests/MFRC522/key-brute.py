#!/usr/bin/env python3

import RPi.GPIO as GPIO
import MFRC522
import signal
import time
import sys

con_reader = True

def end_c_reader(signal, frame):
    global con_reader
    print("Ending the read.")
    con_reader = False
    GPIO.cleanup()

signal.signal(signal.SIGINT, end_c_reader)

c_reader = MFRC522.MFRC522()

print("MFRC522 data reader")
print("Press Ctrl-C to stop.")

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

keys = read_keys_from_file("keys.txt")

while con_reader:
    (status, TagType) = c_reader.MFRC522_Request(c_reader.PICC_REQIDL)

    if status == c_reader.MI_OK:
        print("Card detected")
        (status, uid) = c_reader.MFRC522_Anticoll()

        if status == c_reader.MI_OK:
            print("Card UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3]))

            c_reader.MFRC522_SelectTag(uid)

            authenticated = False
            for key in keys:
                print("Trying key:", key.hex())
                status = c_reader.MFRC522_Auth(c_reader.PICC_AUTHENT1A, 8, key, uid)
                if status == c_reader.MI_OK:
                    authenticated = True
                    print("Key found:", key.hex())
                    c_reader.MFRC522_StopCrypto1()
                    break

            if not authenticated:
                print("No valid key found.")

            time.sleep(0.1)
