#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal, frame):
    global continue_reading
    print("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Function to write data to a specific sector and block
def write_data(data, key, uid):
    # Find the number of blocks required to store the data
    num_blocks = (len(data) + 15) // 16  # Round up to the nearest block
    current_block = 0

    # Authenticate with the card
    status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8 * 4, key, uid)

    if status == MIFAREReader.MI_OK:
        for block_offset in range(num_blocks):
            start_index = block_offset * 16
            end_index = min(start_index + 16, len(data))
            current_data = data[start_index:end_index]

            # Convert the data to bytes and pad with 0xFF if the block is not fully used
            padding_length = 16 - len(current_data)
            current_data += bytes([0xFF] * padding_length)

            # Write the data to the current block
            MIFAREReader.MFRC522_Write(8 * 4 + current_block, current_data)
            print(f"Data written to Block {current_block}: {current_data}")

            current_block += 1

        MIFAREReader.MFRC522_StopCrypto1()
    else:
        print(f"Authentication error for Sector 8")

# Welcome message
print("Welcome to the MFRC522 data read/write example")
print("Press Ctrl-C to stop.")

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

            # Convert the data to bytes (assuming it's in ASCII format)
            data_to_write = b"Hello, RFID!"

            # Write the data to the RFID card
            write_data(data_to_write, key, uid)

            # Read and verify the written data from the RFID card
            # Authenticate with Sector 8 using the same key and UID
            status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8 * 4, key, uid)
            
            if status == MIFAREReader.MI_OK:
                # Read data from the written block
                read_data = MIFAREReader.MFRC522_Read(8 * 4)
                print(f"Data read from Block {8}: {read_data}")

                # Stop Crypto1 communication
                MIFAREReader.MFRC522_StopCrypto1()
            else:
                print("Authentication error for Sector 8")

            # Make sure to stop reading for cards
            continue_reading = False
