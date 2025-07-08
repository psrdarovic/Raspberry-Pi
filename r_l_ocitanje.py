import time
from mfrc522 import SimpleMFRC522
from RPLCD.i2c import CharLCD
from datetime import datetime
import RPi.GPIO as GPIO

GPIO.setwarnings(False)

# Inicijalizacija RFID čitača i LCD ekrana
rfid_reader = SimpleMFRC522()
lcd = CharLCD('PCF8574', 0x27)

# Baza podataka RFID tagova i imena korisnika
users = {
     "1037899540957": "Zuti",  
     "907446455955": "Sivko"
}

def show_datetime():
    """Funkcija za prikaz trenutnog vremena i datuma na LCD-u."""
    now = datetime.now()
    date_time = now.strftime("%d.%m.%Y %H:%M:%S")
    lcd.clear()
    lcd.write_string(date_time)

try:
    while True:
        # Prikazuje trenutno vreme i datum
        show_datetime()
       
        # Čeka RFID unos
        id, text = rfid_reader.read_no_block()  # Koristi read_no_block() da ne blokira petlju
        if id:
            user_id = str(id).strip()  # ID iz kartice
           
            # Proveri korisnika
            if user_id in users:
                name = users[user_id]
                lcd.clear()
                lcd.write_string(f"Papa: {name}")
                print(f"Prepoznao: {name}")
            else:
                lcd.clear()
                lcd.write_string("Nepoznat RFID!")
                print("Nepoznat RFID!")
           
            # Prikazuje ime korisnika na 3 sekunde, zatim se vraća na vreme
            time.sleep(5)
       
        # Pauza pre sledeće provere
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Zaustavljeno od strane korisnika.")
finally:
    lcd.clear()
    print("Ciscenje ekrana i izlazak.")