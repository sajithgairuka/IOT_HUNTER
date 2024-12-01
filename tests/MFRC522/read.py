#!/usr/bin/env python3

import RPi.GPIO as GPIO
import MFRC522
import signal
import time

con_reader = True

def end_c_reader(signal,frame):
    global con_reader
    print("Ending the read.") 
    con_reader = False
    GPIO.cleanup()

signal.signal(signal.SIGINT, end_c_reader)

c_reader = MFRC522.MFRC522()

print("MFRC522 data reader") 
print("Press Ctrl-C to stop.")

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

        if status == c_reader.MI_OK:
            data = c_reader.MFRC522_Read(8)
            
            if data is not None :
                #data_str = " ".join([str(byte) for byte in data])
                data_str = " ".join([format(byte,"02X") for byte in data])
                #data_str = " ".join(chr(byte) for byte in data if byte != 0x00)
                print("Reading the Data:", data_str)
                
            else:
                print("Can't Read") 
            
            c_reader.MFRC522_StopCrypto1()
            
        else:
            print("Authentication error")
            
            
time.sleep(0.1)