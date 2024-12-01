import RPi.GPIO as GPIO
import MFRC522
import signal
import time

con_reader = True

def end_c_reader(signal, frame):
    global con_reader
    print("Ending the read.")
    con_reader = False
    GPIO.cleanup()

signal.signal(signal.SIGINT, end_c_reader)
c_reader = MFRC522.MFRC522()
print("Press Ctrl-C to stop.")

while con_reader:
    (status, TagType) = c_reader.MFRC522_Request(c_reader.PICC_REQIDL)

    if status == c_reader.MI_OK:
        print("Card detected")
        (status, uid) = c_reader.MFRC522_Anticoll()

        if status == c_reader.MI_OK:
            print("Card UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3]))

            c_reader.MFRC522_SelectTag(uid)

            key_found = False
            try:
                with open("keys.txt", 'r') as file:
                    for line in file:
                        line = line.strip()
                        if line:
                            key = bytes.fromhex(line.replace(" ", ""))
                            if len(key) == 6:
                                print("Trying key:", key.hex())
                                status = c_reader.MFRC522_Auth(c_reader.PICC_AUTHENT1A, 8, key, uid)
                                if status == c_reader.MI_OK:
                                    print("Key found:", key.hex())
                                    key_found = True
                                    break  # Exit the loop if any valid key is found

                if not key_found:
                    print("No valid key found.")
            except FileNotFoundError:
                print("File 'keys.txt' not found.")

            time.sleep(0.1)
