import binascii
import time
import signal
import sys
import board
import busio
import adafruit_pn532.i2c as PN532_I2C

# Create I2C bus.
i2c = busio.I2C(board.SCL, board.SDA)

# Create an instance of the PN532 class for I2C communication.
pn532 = PN532_I2C.PN532_I2C(i2c, debug=False)

# Configure the key to use for writing to the MiFare card. You probably don't
# need to change this from the default below unless you know your card has a
# different key associated with it.
CARD_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

# Number of seconds to delay after reading and writing data.
DELAY = 0.5

def close(signal, frame):
    print('Program closed.')
    sys.exit(0)

signal.signal(signal.SIGINT, close)

print('PN532 NFC RFID 13.56MHz Card Reader and Writer')

# Define the data you want to write to the card to reset it (all zeros).
reset_data = b'\x00' * 16

try:
    while True:
        # Wait for a card to be available
        uid = pn532.read_passive_target()
        # Try again if no card found
        if uid is None:
            continue
        # Found a card, now try to write zeros to block 4 to reset it
        print('')
        uid_decimal = ', '.join(str(byte) for byte in uid)
        print('Card UID: {0}'.format(uid_decimal))
        
        # Authenticate for writing to block 4
        if not pn532.mifare_classic_authenticate_block(uid, 4, 0x61, CARD_KEY):
            print('Failed to authenticate with card!')
            continue
        
        # Write zeros to block 4 to reset it
        if not pn532.mifare_classic_write_block(4, reset_data):
            print('Failed to reset data on card!')
            continue
        
        print('Data reset on card.')
        
        # Close the program after successful reset
        sys.exit(0)
except KeyboardInterrupt:
    # Handle Ctrl+C gracefully and exit
    print('Ctrl+C pressed. Program closed.')
    sys.exit(0)
except Exception as e:
    print('Error:', e)
    sys.exit(1)
