import RPi.GPIO as GPIO
import mylib.MFRC522 as MFRC522
import signal
import argparse
import sys

def parse_args(args):

    parser = argparse.ArgumentParser(prog='frame.py rfid_write', 
                                    formatter_class=argparse.RawDescriptionHelpFormatter,
                                    description='This script writes the data to a Mifare Classic RFID card.',
                                    epilog="""Example usage:

    frame.py rfid_write -w "hello" """)
    parser.add_argument('-w','--write_data', type=str,help='The data to write to the MiFare card')

    args = parser.parse_args(args)
    return args


def end_read(signal, frame):
    global continue_reading
    print("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()
    sys.exit(0)

def all_code(args):
    signal.signal(signal.SIGINT, end_read)
    continue_reading = True
    MIFAREReader = MFRC522.MFRC522()

    while continue_reading:  
        (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
        if status == MIFAREReader.MI_OK:
            print("\nRFID Card Writer")
    
        (status, uid) = MIFAREReader.MFRC522_Anticoll()
        if status == MIFAREReader.MI_OK:
            print("Card read UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3]))
    
            key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
      
            MIFAREReader.MFRC522_SelectTag(uid)
            status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)
            #print("\n")

            if status == MIFAREReader.MI_OK:
                data = []
                meaningful_data = args.write_data
                meaningful_data_bytes = bytearray(meaningful_data.encode("utf-8"))
                for x in range(0, 16):
                    if x < len(meaningful_data_bytes):
                        data.append(meaningful_data_bytes[x])
                    else:
                        data.append(0xFF)
                
                MIFAREReader.MFRC522_Write(8, data)
                #print("It now looks like this:")
                read_data = MIFAREReader.MFRC522_Read(8)
                #hex_data = binascii.hexlify(read_data).decode("utf-8")
                #print(hex_data)
                read_data_str = "".join([chr(byte) for byte in read_data if byte != 0xFF])
                print('Data written to card:', read_data_str)

                MIFAREReader.MFRC522_StopCrypto1()
                continue_reading = False
            else:
                print("Authentication error")

def module_main(args):
    args = parse_args(args)
    all_code(args)
