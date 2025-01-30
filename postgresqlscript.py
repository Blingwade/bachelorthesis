# imports
import docker
import psycopg2
import time

def manage_postgresql_with_docker():
    # Docker-Client initialisieren
    client = docker.from_env()

    try:
        # PostgreSQL-Container starten
        print("Starte PostgreSQL-Container...")
        container = client.containers.run(
            image="postgres:latest",
            name="postgresql-container",
            environment={
                "POSTGRES_USER": "admin",
                "POSTGRES_PASSWORD": "password",
                "POSTGRES_DB": "example_db",
            },
            ports={"5432/tcp": 5432},
            detach=True,
        )
        print(f"PostgreSQL-Container gestartet. Container-ID: {container.id}")

        # Wartezeit, bis der Container bereit ist
        print("Warte, bis der PostgreSQL-Container bereit ist...")
        time.sleep(10)

        # Verbindung zur PostgreSQL-Datenbank herstellen
        print("Stelle Verbindung zur Datenbank her...")
        conn = psycopg2.connect(
            dbname="example_db",
            user="admin",
            password="password",
            host="localhost",
            port=5432
        )
        cur = conn.cursor()

        # Tabelle erstellen
        print("Erstelle Tabelle...")
        create_table_query = """
        CREATE TABLE IF NOT EXISTS sensor_data (
            id SERIAL PRIMARY KEY,
            sensor_name VARCHAR(50),
            value FLOAT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cur.execute(create_table_query)
        conn.commit()
        print("Tabelle erfolgreich erstellt.")

        # Daten einfügen
        print("Füge Beispieldaten hinzu...")
        insert_data_query = """
        INSERT INTO sensor_data (sensor_name, value)
        VALUES (%s, %s);
        """
        data = [
            ("temperature_sensor", 22.5),
            ("temperature_sensor", 23.1),
            ("humidity_sensor", 45.3),
            ("humidity_sensor", 46.7),
            ("pressure_sensor", 1013.2),
        ]
        cur.executemany(insert_data_query, data)
        conn.commit()
        print(f"{cur.rowcount} Zeilen eingefügt.")

        # Daten abfragen
        print("Frage Temperaturdaten ab...")
        query = "SELECT * FROM sensor_data WHERE sensor_name = %s;"
        cur.execute(query, ("temperature_sensor",))
        results = cur.fetchall()

        for row in results:
            print(row)

    except Exception as e:
        print(f"Fehler: {e}")

    finally:
        # Cursor und Verbindung schließen
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
            print("Verbindung zur PostgreSQL-Datenbank geschlossen.")

        # Container stoppen und löschen
        print("Stoppe den Container...")
        try:
            container.stop()
            container.remove()
            print("Container erfolgreich gestoppt und gelöscht.")
        except Exception as e:
            print(f"Fehler beim Stoppen/Löschen des Containers: {e}")

if __name__ == "__main__":
    manage_postgresql_with_docker()
