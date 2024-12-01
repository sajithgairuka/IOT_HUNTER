import binascii
import time
import signal
import sys
import board
import busio
import adafruit_pn532.i2c as PN532_I2C
import argparse

def close(signal, frame):
    print('Program closed.')
    sys.exit(0)

def parse_args(args):
    parser = argparse.ArgumentParser(prog='frame.py nfc_dump', 
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description='This script dumps the data from a Mifare Classic NFC card.',
                                 epilog="""Example usage:

            frame.py nfc_dump -o "data_dumps/nfc_dump.txt" """)

    parser.add_argument('-o', '--output', help='Lacation to save the data with file name.', default='data_dumps/nfc_dump.txt',type=str) 

    args = parser.parse_args(args)
    return args

def code(args):
    i2c = busio.I2C(board.SCL, board.SDA)
    pn532 = PN532_I2C.PN532_I2C(i2c, debug=False)
    CARD_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    signal.signal(signal.SIGINT, close)
    DELAY = 0.5

    print('PN532 NFC Card Data Dumpper')

    save_location = args.output

    with open(save_location, 'a') as file:
        while True:
            uid = pn532.read_passive_target()
            if uid is None:
                continue
            print('')
            uid_decimal = ', '.join(str(byte) for byte in uid)
            print('Card UID: {0}'.format(uid_decimal))
            if not pn532.mifare_classic_authenticate_block(uid, 4, 0x61, CARD_KEY):
                print('Failed to authenticate with card!')
                continue
            data = pn532.mifare_classic_read_block(4)
            if data is None:
                print('Failed to read data from card!')
                continue
            user_data = binascii.hexlify(data).decode("utf-8")
            print('User Data: {0}'.format(user_data))
            save_data = f"{uid_decimal} : {user_data}\n"
            file.write(save_data)
            print("Data Saved Location : data_dumps/nfc_dump.txt")
        
            time.sleep(DELAY)
            
def module_main(args):
    args = parse_args(args)
    code(args)