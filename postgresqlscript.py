# imports
import docker
import psycopg2
import time
import json

def manage_postgresql_with_docker():
    # Docker-Client initialisieren
    client = docker.from_env()

    try:
        # PostgreSQL-Container starten
        print("starting postgreSQL container...")
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
        print(f"PostgreSQL container started. Container-ID: {container.id}")

        # Wartezeit, bis der Container bereit ist
        print("waiting for the container...")
        time.sleep(10)

        # Verbindung zur PostgreSQL-Datenbank herstellen
        print("connecting to database...")
        conn = psycopg2.connect(
            dbname="example_db",
            user="admin",
            password="password",
            host="localhost",
            port=5432
        )
        cur = conn.cursor()

        # Tabelle erstellen
        print("creating table...")
        create_table_query = """
        CREATE TABLE IF NOT EXISTS example_table (
            tag1 varchar(50),
            field1 float,
            field2 float,
            field3 float,
            timestamp int
        );
        """
        cur.execute(create_table_query)
        conn.commit()
        print("table created successfully")

        # Daten einfügen
        print("inserting example data...")
        insert_data_query = """
        INSERT INTO example_table (tag1, field1, field2, field3, timestamp)
        VALUES (%s, %s, %s, %s, %s);
        """
        f = open("postgresqldata.txt" , "r")


        # take lines from the file, separate them at every "," , delete /n and convert to tuple
        data = [tuple(line.strip('\n').split(",")) for line in f.readlines()] # most cursed line of code i have ever written
        f.close()
  
        cur.executemany(insert_data_query, data)
        conn.commit()
        print(f"{cur.rowcount} Zeilen eingefügt.")

        # Daten abfragen
        print("Frage Beispieldaten ab...")

        # import query


        queryfile = open("queries.json", "r")
        query = json.loads(queryfile.read())["sum"]["postgres"]
        queryfile.close()
        cur.execute(query)
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

            input("wait for input to close database")
            container.stop()
            container.remove()
            print("Container stopped and deleted.")
        except Exception as e:
            print(f"Exception while stopping/deleting the container: {e}")

if __name__ == "__main__":
    manage_postgresql_with_docker()
