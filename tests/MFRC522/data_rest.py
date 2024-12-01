#!/usr/bin/env python3

import RPi.GPIO as GPIO
import MFRC522
import signal

con_reader = True

def end_c_reader(signal,frame):
    global con_reader
    print("Ending the read.")
    con_reader = False
    GPIO.cleanup()

signal.signal(signal.SIGINT, end_c_reader)

c_reader = MFRC522.MFRC522()

while con_reader:
       
    (status,TagType) = c_reader.MFRC522_Request(c_reader.PICC_REQIDL)

    if status == c_reader.MI_OK:
        print("Card detected")
    
    (status,uid) = c_reader.MFRC522_Anticoll()

    if status == c_reader.MI_OK:

        print("Card UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3]))
    
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        
        c_reader.MFRC522_SelectTag(uid)

        status = c_reader.MFRC522_Auth(c_reader.PICC_AUTHENT1A, 8, key, uid)
        print("\n")

        if status == c_reader.MI_OK:

            data = []
            # Fill the data with 0xFF
            for x in range(0,16):
                data.append(0xFF)

            print("Sector 8 Reading:")
            c_reader.MFRC522_Read(8)
            print("\n")

            print("Sector 8 will now be filled with 0xFF:")
            c_reader.MFRC522_Write(8, data)
            print(data)
            print("\n") 

            print("After sector 8 filling:")
            c_reader.MFRC522_Read(8)
            print("\n")

            data = []
            # Fill the data with 0x00
            for x in range(0,16):
                data.append(0x00)

            print("Now we fill it with 0x00:")
            c_reader.MFRC522_Write(8, data)
            print(data)
            print("\n")

            print("It is now empty:")
            c_reader.MFRC522_Read(8)
            print("\n")

            c_reader.MFRC522_StopCrypto1()

            con_reader = False
        else:
            print("Authentication error")
