#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal
import binascii
import sys

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal, frame):
    global continue_reading
    print("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Function to read data from a specific sector
def read_sector(sector, key, uid):
    status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, sector * 4, key, uid)

    if status == MIFAREReader.MI_OK:
        for block in range(sector * 4, sector * 4 + 4):
            data = MIFAREReader.MFRC522_Read(block)
            if data is not None:
                hex_data = binascii.hexlify(data).decode("utf-8")
                print(f"Data from Sector {sector}, Block {block % 4}: {hex_data}")
            MIFAREReader.MFRC522_StopCrypto1()
        return True
    else:
        return False

# Welcome message
print("Welcome to the MFRC522 data read example")
print("Press Ctrl-C to stop.")

# Redirect stderr to suppress error messages
original_stderr = sys.stderr
sys.stderr = open("/dev/null", "w")

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Restore stderr
sys.stderr = original_stderr

# This loop keeps checking for chips. If one is near, it will get the UID and authenticate
while continue_reading:
    # Scan for cards
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print("Card detected")

        # Get the UID of the card
        (status, uid) = MIFAREReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == MIFAREReader.MI_OK:
            # Print UID
            print("Card read UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3]))

            # This is the default key for authentication
            key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

            # Select the scanned tag
            MIFAREReader.MFRC522_SelectTag(uid)

            # Read data from each sector using the default key
            for sector in range(0, 16):
                if read_sector(sector, key, uid):
                    continue_reading = False
                    break
