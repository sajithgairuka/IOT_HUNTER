import binascii
import time
import signal
import sys
import board
import busio
import adafruit_pn532.i2c as PN532_I2C
import argparse

def parse_args(args):

    parser = argparse.ArgumentParser(prog="frame.py nfc_reset",
                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                description='Reset NFC card Data.',
                                epilog="""Example usage:

    frame.py nfc_reset """)

    args = parser.parse_args(args)
    return args

def close(signal, frame):
    print('Program closed.')
    sys.exit(0)


def all_code():
    i2c = busio.I2C(board.SCL, board.SDA)
    pn532 = PN532_I2C.PN532_I2C(i2c, debug=False)
    CARD_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    DELAY = 0.5
    signal.signal(signal.SIGINT, close)
    print('PN532 NFC Card Reset Program')
    reset_data = b'\x00' * 16

    try:
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
            if not pn532.mifare_classic_write_block(4, reset_data):
                print('Failed to reset data on card!')
                continue     
            print('Data reset on card.')
            time.sleep(DELAY)
            sys.exit(0)
    except KeyboardInterrupt:
        print('Ctrl+C pressed. Program closed.')
        sys.exit(0)
    except Exception as e:
        print('Error:', e)
        sys.exit(1)

def module_main(args):
    args=parse_args(args)
    all_code()