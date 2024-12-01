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
    parser = argparse.ArgumentParser(prog="frame.py nfc_write",
                                    formatter_class=argparse.RawDescriptionHelpFormatter,
                                    description='Write NFC card Data.',
                                    epilog="""Example usage:

            frame.py nfc_write -w "hi" """)

    parser.add_argument('-w', "--write_data", type=str, required=True,help='The data to write to the MiFare card')

    args = parser.parse_args(args)
    return args

def write_nfc_data(args):

    i2c = busio.I2C(board.SCL, board.SDA)
    pn532 = PN532_I2C.PN532_I2C(i2c, debug=False)
    CARD_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    DELAY = 0.5
    signal.signal(signal.SIGINT, close)

    print('PN532 NFC Card Writer')

    write_data = args.write_data.encode('utf-8')

    try:
        while True:
            uid = pn532.read_passive_target()
            # Try again if no card found
            if uid is None:
                continue
            print('')
            uid_decimal = ', '.join(str(byte) for byte in uid)
            print('Card UID: {0}'.format(uid_decimal))
    
            if not pn532.mifare_classic_authenticate_block(uid, 4, 0x61, CARD_KEY):
                print('Failed to authenticate with card!')
                continue
            if len(write_data) < 16:
                write_data = write_data.ljust(16, b' ')
            elif len(write_data) > 16:
                write_data = write_data[:16]
            if not pn532.mifare_classic_write_block(4, write_data):
                print('Failed to write data to card!')
                continue
        
            print('Data written to card: {0}'.format(write_data.decode("utf-8")))
            sys.exit(0)
    except KeyboardInterrupt:
        print('Ctrl+C pressed. Program closed.')
        sys.exit(0)
    except Exception as e:
        print('Error:', e)
        sys.exit(1)


def module_main(args):
    args=parse_args(args)
    write_nfc_data(args)

