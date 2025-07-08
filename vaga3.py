import RPi.GPIO as GPIO
from hx711 import HX711

# Definicija pinova za HX711
dt = 5  # Data pin
sck = 6  # Clock pin

# Onemogućavanje upozorenja i postavljanje GPIO načina
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Inicijalizacija HX711
hx711 = HX711(dout_pin=dt, pd_sck_pin=sck)

# Funkcija za očitavanje sirovih podataka
def read_raw_data(num_samples=10):
    raw_data = hx711.get_raw_data_mean(num_samples)
    return raw_data

# Tariranje - očitavanje offseta
def tare(num_samples=10):
    print("Tariranje... Molim, ostavi vagu praznom.")
    offset = read_raw_data(num_samples)
    print(f"Offset postavljen na: {offset}")
    return offset

# Kalibracija - izračun kalibracijskog faktora
def calibrate(known_weight, offset, num_samples=10):
    print(f"Stavi poznatu masu od {known_weight}g na vagu.")
    input("Pritisni Enter kada si spreman.")
    raw_data = read_raw_data(num_samples)
    calibration_factor = (raw_data - offset) / known_weight
    print(f"Kalibracijski faktor: {calibration_factor}")
    return calibration_factor

# Očitavanje težine uz offset i kalibracijski faktor
def get_weight(offset, calibration_factor, num_samples=10):
    raw_data = read_raw_data(num_samples)
    weight = (raw_data - offset) / calibration_factor
    return weight

try:
    # Dijagnostika sirovih podataka
    print("Dijagnostika: očitavanje sirovih podataka...")
    for _ in range(5):
        raw_data = read_raw_data(10)
        print(f"Raw data: {raw_data}")

    # Tariranje
    offset = tare()

    # Kalibracija
    known_weight = float(input("Unesi težinu poznatog objekta (g) za kalibraciju: "))
    calibration_factor = calibrate(known_weight, offset)

    # Očitavanje težine
    print("Postavi težinu na vagu za očitanje.")
    while True:
        weight = get_weight(offset, calibration_factor, 10)
        print(f"Težina: {weight:.2f} g")
except KeyboardInterrupt:
    print("Izlazim iz programa.")
finally:
    # Isključenje HX711 i čišćenje GPIO
    hx711.power_down()
    GPIO.cleanup()
    
