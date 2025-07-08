import sqlite3

# Povezivanje s bazom podataka
db_file = "vaga_data.db"  # Naziv vaše baze
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

try:
    # Brisanje svih podataka iz tablice
    cursor.execute("DELETE FROM podaci;")
    conn.commit()
    print("Svi podaci su obrisani iz tablice.")
except Exception as e:
    print(f"Došlo je do greške: {e}")
finally:
    conn.close()