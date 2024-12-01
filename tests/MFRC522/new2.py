#!/usr/bin/env python3

import RPi.GPIO as GPIO
import MFRC522
import signal
import time
import logging

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

# Suppress error messages from MFRC522_Auth function
logger = logging.getLogger('MFRC522')
logger.setLevel(logging.CRITICAL)

while con_reader:
    (status, TagType) = c_reader.MFRC522_Request(c_reader.PICC_REQIDL)

    if status == c_reader.MI_OK:
        print("Card detected")
    (status, uid) = c_reader.MFRC522_Anticoll()

    if status == c_reader.MI_OK:
        print("Card UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3]))

        c_reader.MFRC522_SelectTag(uid)

        for sector in range(16):
            # Authenticate with default key
            key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

            # Suppress error messages from MFRC522_Auth function
            logger = logging.getLogger('MFRC522')
            logger.setLevel(logging.CRITICAL)
            status = c_reader.MFRC522_Auth(c_reader.PICC_AUTHENT1A, sector * 4, key, uid)
            logger.setLevel(logging.ERROR)

            if status == c_reader.MI_OK:
                # Directly read data from each block in the sector
                for block in range(sector * 4, sector * 4 + 4):
                    data = c_reader.MFRC522_Read(block)
                    if data is not None:
                        data_str = " ".join([format(byte, "02X") for byte in data])
                        print(f"Data from Sector {sector}, Block {block % 4}: {data_str}")
                    else:
                        print(f"Can't Read Sector {sector}, Block {block % 4}")

                c_reader.MFRC522_StopCrypto1()

        time.sleep(0.1)
