import RPi.GPIO as GPIO
import MFRC522

def reset_card():
    # Create an object of the class MFRC522
    MIFAREReader = MFRC522.MFRC522()

    # This is the default key for authentication
    default_key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

    # Scan for cards
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print("Card detected")

        # Get the UID of the card
        (status, uid) = MIFAREReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == MIFAREReader.MI_OK:
            # Print UID
            print("Card read UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3]))

            # Select the scanned tag
            MIFAREReader.MFRC522_SelectTag(uid)

            # Reset the card by writing 0x00 to all data blocks
            for sector in range(16):
                for block in range(sector * 4, sector * 4 + 4):
                    MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, block, default_key, uid)
                    MIFAREReader.MFRC522_Write(block, [0x00] * 16)
                    MIFAREReader.MFRC522_StopCrypto1()
                    print(f"Reset data in Sector {sector}, Block {block % 4}")

            # Stop crypto after resetting all sectors
            MIFAREReader.MFRC522_StopCrypto1()

            print("Card reset successful.")

# Call the reset_card() function to attempt resetting the card
reset_card()

# Cleanup GPIO
GPIO.cleanup()
