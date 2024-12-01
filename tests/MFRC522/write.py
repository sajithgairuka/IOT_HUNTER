import RPi.GPIO as GPIO
import MFRC522
import signal
import binascii

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal, frame):
    global continue_reading
    print("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# This loop keeps checking for chips. If one is near, it will get the UID and authenticate
while continue_reading:
    
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
    
        # This is the default key for authentication
        key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        
        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Authenticate
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)
        print("\n")

        # Check if authenticated
        if status == MIFAREReader.MI_OK:

            # Variable for the data to write
            data = []

            # Define the meaningful data
            meaningful_data = "hasith"

            # Convert meaningful data to bytes (assuming UTF-8 encoding)
            meaningful_data_bytes = bytearray(meaningful_data.encode("utf-8"))

            # Fill the data with meaningful data
            for x in range(0, 16):
                if x < len(meaningful_data_bytes):
                    data.append(meaningful_data_bytes[x])
                else:
                    data.append(0xFF)
                
            print("Sector 8 will now be filled with meaningful data:")
            # Write the data
            MIFAREReader.MFRC522_Write(8, data)

            print("It now looks like this:")
            # Check to see if it was written
            read_data = MIFAREReader.MFRC522_Read(8)
            hex_data = binascii.hexlify(read_data).decode("utf-8")
            print(hex_data)

            # Stop
            MIFAREReader.MFRC522_StopCrypto1()

            # Make sure to stop reading for cards
            continue_reading = False
        else:
            print("Authentication error")
