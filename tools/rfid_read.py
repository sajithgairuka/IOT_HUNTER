import RPi.GPIO as GPIO
import mylib.MFRC522 as MFRC522
import signal
import time
import argparse
import sys

def parse_args(args):
    parser = argparse.ArgumentParser(prog='frame.py rfid_read', 
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description='This script reads the data from a Mifare Classic RFID card.',
                                 epilog="""Example usage:

            frame.py rfid_read """)
    args = parser.parse_args(args)
    return args

def end_c_reader(signal,frame):
    global con_reader
    print("Ending the read.") 
    con_reader = False
    GPIO.cleanup()
    sys.exit(0)

def all_code():
    signal.signal(signal.SIGINT, end_c_reader)
    c_reader = MFRC522.MFRC522()
    print("Press Ctrl-C to stop.")
    con_reader = True

    while con_reader:   
        (status,TagType) = c_reader.MFRC522_Request(c_reader.PICC_REQIDL)

        if status == c_reader.MI_OK:
            print("\nRFID Card Reader")     
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



def module_main(args):
    args=parse_args(args)
    all_code()