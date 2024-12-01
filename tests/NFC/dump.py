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

# Number of seconds to delay after reading data.
DELAY = 0.5

def close(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, close)

print('PN532 NFC RFID 13.56MHz Card Reader')
with open('dump.txt', 'a') as file:
    while True:
        # Wait for a card to be available
        uid = pn532.read_passive_target()
        # Try again if no card found
        if uid is None:
            continue
        # Found a card, now try to read block 4
        print('')
        uid_decimal = ', '.join(str(byte) for byte in uid)
        print('Card UID: {0}'.format(uid_decimal))
        # Authenticate and read block 4
        if not pn532.mifare_classic_authenticate_block(uid, 4, 0x61, CARD_KEY):
            print('Failed to authenticate with card!')
            continue
        data = pn532.mifare_classic_read_block(4)
        if data is None:
            print('Failed to read data from card!')
            continue
        # Parse out the block data as hexadecimal
        user_data = binascii.hexlify(data).decode("utf-8")
        print('User Data: {0}'.format(user_data))
        
        # Write the UID and user data to the dump.txt file
        #file.write(f'Card UID: {uid_decimal}\n')
        #file.write(f'User Data: {user_data}\n\n')
        save_data = f"{uid_decimal} : {user_data}\n"
        file.write(save_data)
        
        time.sleep(DELAY)
