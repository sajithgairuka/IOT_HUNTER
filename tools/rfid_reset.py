import RPi.GPIO as GPIO
import mylib.MFRC522 as MFRC522
import signal
import argparse
import sys
    
def parse_args(args):
    parser = argparse.ArgumentParser(prog='frame.py rfid_read', 
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description='This script reset the data from a mifare classic RFID card.',
                                 epilog="""Example usage:

            frame.py rfid_reset """)
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
    con_reader = True

    while con_reader:   
        (status,TagType) = c_reader.MFRC522_Request(c_reader.PICC_REQIDL)

        if status == c_reader.MI_OK:
            print("RFID Card Reset Program Started")
    
        (status,uid) = c_reader.MFRC522_Anticoll()

        if status == c_reader.MI_OK:
            print("Card UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3]))
    
            key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        
            c_reader.MFRC522_SelectTag(uid)

            status = c_reader.MFRC522_Auth(c_reader.PICC_AUTHENT1A, 8, key, uid)
            if status == c_reader.MI_OK:
                data = []
                # Fill the data with 0xFF
                for x in range(0,16):
                    data.append(0xFF)
                print("Reading: ....")
                c_reader.MFRC522_Read(8)
                print("Sectors now filled with 0xFF:")
                c_reader.MFRC522_Write(8, data)
                print(data)
                c_reader.MFRC522_Read(8)
                data = []
                # Fill the data with 0x00
                for x in range(0,16):
                    data.append(0x00)

                print("Now we fill it with 0x00:")
                print("It is now empty:")
                c_reader.MFRC522_Write(8, data)
                print(data)
                c_reader.MFRC522_Read(8)
                c_reader.MFRC522_StopCrypto1()
                con_reader = False
            else:
                print("Authentication error")

def module_main(args):
    args=parse_args(args)
    all_code()