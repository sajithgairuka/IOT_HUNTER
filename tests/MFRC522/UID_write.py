import RPi.GPIO as GPIO
import MFRC522
import signal
import binascii

continue_reading = True

def end_read(signal, frame):
    global continue_reading
    print("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()

signal.signal(signal.SIGINT, end_read)

MIFAREReader = MFRC522.MFRC522()

# This function writes the new UID to the card
def write_new_uid(uid):
    key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

    # Select the scanned tag
    MIFAREReader.MFRC522_SelectTag(uid)

    # Authenticate with the default key
    status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

    if status == MIFAREReader.MI_OK:
        # Write the new UID to sector 8 (assuming the new UID is 4 bytes)
        new_uid = [0x12, 0x34, 0x56, 0x78]
        # Pad the new_uid to be 16 bytes long
        new_uid.extend([0] * (16 - len(new_uid)))
        MIFAREReader.MFRC522_Write(8, new_uid)
        print("New UID written to sector 8:", binascii.hexlify(bytearray(new_uid)).decode("utf-8"))
    else:
        print("Authentication error")

    # Stop crypto and cleanup
    MIFAREReader.MFRC522_StopCrypto1()
    GPIO.cleanup()

while continue_reading:
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    if status == MIFAREReader.MI_OK:
        print("Card detected")

    (status, uid) = MIFAREReader.MFRC522_Anticoll()

    if status == MIFAREReader.MI_OK:
        print("Card read UID:", binascii.hexlify(bytearray(uid)).decode("utf-8"))

        # Call the function to write the new UID
        write_new_uid(uid)

        # Exit the loop after changing the UID of the card
        continue_reading = False
