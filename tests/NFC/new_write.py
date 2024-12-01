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

# Define the data you want to write to the card.
# Make sure it's exactly 16 bytes long.
write_data = 'Hello, NFC!    '.encode('utf-8')  # Example: Pad to 16 bytes with spaces

try:
    while True:
        # Wait for a card to be available
        uid = pn532.read_passive_target()
        # Try again if no card found
        if uid is None:
            continue
        # Found a card, now try to write to block 4
        print('')
        uid_decimal = ', '.join(str(byte) for byte in uid)
        print('Card UID: {0}'.format(uid_decimal))
        
        # Authenticate for writing to block 4
        if not pn532.mifare_classic_authenticate_block(uid, 4, 0x61, CARD_KEY):
            print('Failed to authenticate with card!')
            continue
        
        # Check if write_data is exactly 16 bytes long, pad or truncate as needed
        if len(write_data) < 16:
            write_data = write_data.ljust(16, b' ')  # Pad with spaces
        elif len(write_data) > 16:
            write_data = write_data[:16]  # Truncate
        
        # Write the data to block 4
        if not pn532.mifare_classic_write_block(4, write_data):
            print('Failed to write data to card!')
            continue
        
        print('Data written to card: {0}'.format(write_data.decode("utf-8")))
        
        # Close the program after successful write
        sys.exit(0)
except KeyboardInterrupt:
    # Handle Ctrl+C gracefully and exit
    print('Ctrl+C pressed. Program closed.')
    sys.exit(0)
except Exception as e:
    print('Error:', e)
    sys.exit(1)
