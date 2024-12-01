import RPi.GPIO as GPIO
import mylib.MFRC522 as MFRC522
import signal
import time
import sys
import argparse

def end_c_reader(signal,frame):
    global con_reader
    print("Ending the read.")
    con_reader = False
    GPIO.cleanup()
    sys.exit(0)

def parse_args(args):
    parser = argparse.ArgumentParser(prog='frame.py rfid_dump', 
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description='This script dumps the data from a Mifare Classic card.',
                                 epilog="""Example usage:

            frame.py rfid_dump -o "data_dumps/rfid_dump.txt" """)

    parser.add_argument('-o', '--output', help='Output file name.', default="data_dumps/rfid_dump.txt",type=str) 
    args = parser.parse_args(args)
    return args

def coding(args):

    con_reader = True
    signal.signal(signal.SIGINT, end_c_reader)
    c_reader = MFRC522.MFRC522()

    dumpfile = args.output

    while con_reader:
        (status,TagType) = c_reader.MFRC522_Request(c_reader.PICC_REQIDL)

        if status == c_reader.MI_OK:
            print("Card detected") 

        (status,uid) = c_reader.MFRC522_Anticoll()

        if status == c_reader.MI_OK:
            #print("Card UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3]))
            card_uid = ",".join([str(byte) for byte in uid])
            print("Card UID: %s" % card_uid)
            key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
            c_reader.MFRC522_SelectTag(uid)
        
            status = c_reader.MFRC522_Auth(c_reader.PICC_AUTHENT1A, 8, key, uid)
        
            if status == c_reader.MI_OK:
                data = c_reader.MFRC522_Read(8)
        
                if data is not None :
                    #data_str = ",".join([str(byte) for byte in data])
                    data_str = " ".join([format(byte,"02X") for byte in data])
                
                    save_data = f"{card_uid} : {data_str}\n"
                
                    with open(dumpfile,"a") as file:
                        file.write(save_data)
                        print("Dump Data:", data_str)
                        print("Data Saved Location : data_dumps/rfid_dump.txt")              
                else:
                    print("error")  
            
                c_reader.MFRC522_StopCrypto1()        
        
            else:
                print("Auth error")
        
    time.sleep(0.1)

def module_main(args):
    args = parse_args(args)
    coding(args)