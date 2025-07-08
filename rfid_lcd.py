import time
from mfrc522 import SimpleMFRC522
from RPLCD.i2c import CharLCD
from datetime import datetime

# Inicijalizacija RFID čitača i LCD ekrana
rfid_reader = SimpleMFRC522()
lcd = CharLCD('PCF8574', 0x27)

# Baza podataka RFID tagova i imena korisnika
users = {
    "1037899540957": "Zuti",  
    "907446455955": "Sivko"
}

try:
    while True:
        lcd.clear()
        lcd.write_string("Prisloni RFID...")
        print("Cekanje na RFID...")
       
        # Čitaj RFID karticu
        id, text = rfid_reader.read()
        user_id = str(id).strip()  # ID iz kartice
       
        # Proveri korisnika
        if user_id in users:
            name = users[user_id]
            lcd.clear()
           
            # Datum i vreme
            now = datetime.now()
            date_time = now.strftime("%d.%m.%Y %H:%M")
           
            # Prikaz na LCD
            lcd.write_string(f"{name} \n{date_time}")
            print(f"Prepoznao: {name} - {date_time}")
        else:
            lcd.clear()
            lcd.write_string("Nepoznat RFID!")
            print("Nepoznat RFID!")
       
        time.sleep(2)  # Pauza pre sledećeg skeniranja

except KeyboardInterrupt:
    print("Zaustavljeno od strane korisnika.")
finally:
    lcd.clear()
    print("Ciscenje ekrana i izlazak.")