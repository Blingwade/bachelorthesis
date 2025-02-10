# imports
import docker
import psycopg2
import time
import json

def manage_postgresql_with_docker():
    # Docker-Client initialisieren
    client = docker.from_env()
    starttime = 0
    endtime = 0
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

        # Tabellen erstellen
        print("creating table...")
        create_table_query = """
        CREATE TABLE IF NOT EXISTS example_table0 (
            measurement varchar(50),
            tag1 varchar(50),
            field1 float,
            field2 float,
            field3 float,
            timestamp int
        );
        CREATE TABLE IF NOT EXISTS example_table1 (
            measurement varchar(50),
            tag1 varchar(50),
            field1 float,
            field2 float,
            field3 float,
            timestamp int
        );
        CREATE TABLE IF NOT EXISTS example_table2 (
            measurement varchar(50),
            tag1 varchar(50),
            field1 float,
            field2 float,
            field3 float,
            timestamp int
        );
        CREATE INDEX idx_field1 ON example_table1(field1);
        """
       
        cur.execute(create_table_query)
        conn.commit()
        print("table created successfully")

        # Daten einfügen
        print("inserting example data...")
        insert_data_query0 = """
        INSERT INTO example_table0 (measurement, tag1, field1, field2, field3, timestamp)
        VALUES (%s,%s,%s,%s,%s,%s);
        """
        insert_data_query1 = """
        INSERT INTO example_table1 (measurement, tag1, field1, field2, field3, timestamp)
        VALUES (%s,%s,%s,%s,%s,%s);
        """
        insert_data_query2  = """
        INSERT INTO example_table2 (measurement, tag1, field1, field2, field3, timestamp)
        VALUES (%s,%s,%s,%s,%s,%s);
        """
        f = open("postgresqldata0.txt" , "r")
        # take lines from the file, separate them at every "," , delete /n and convert to tuple
        data0 = [tuple(line.strip('\n').split(",")) for line in f.readlines()] # most cursed line of code i have ever written
        #data = [line.strip('\n') for line in f.readlines()]
        data0_out = []
        for t in data0:
            t_out = []
            i = 0
            for tE in t:
                if tE == 'NULL':
                    t_out.append(None)
                else:
                    t_out.append(tE)
                i += 1
            data0_out.append(tuple(t_out))  

        f.close()
        print(data0_out)
        cur.executemany(insert_data_query0, data0_out)

        f = open("postgresqldata1.txt" , "r")
        # take lines from the file, separate them at every "," , delete /n and convert to tuple
        data1 = [tuple(line.strip('\n').split(",")) for line in f.readlines()] # most cursed line of code i have ever written
        #data = [line.strip('\n') for line in f.readlines()]
        data1_out = []
        for t in data1:
            t_out = []
            i = 0
            for tE in t:
                if tE == 'NULL':
                    t_out.append(None)
                else:
                    t_out.append(tE)
                i += 1
            data1_out.append(tuple(t_out))  

        f.close()

        print(data1_out)

        cur.executemany(insert_data_query1, data1_out)

        f = open("postgresqldata2.txt" , "r")

        # take lines from the file, separate them at every "," , delete /n and convert to tuple
        data2 = [tuple(line.strip('\n').split(",")) for line in f.readlines()] # most cursed line of code i have ever written
        #data = [line.strip('\n') for line in f.readlines()]
        data2_out = []
        for t in data2:
            t_out = []
            i = 0
            for tE in t:
                if tE == 'NULL':
                    t_out.append(None)
                else:
                    t_out.append(tE)
                i += 1
            data2_out.append(tuple(t_out))  

        f.close()
        print(data2_out)
        cur.executemany(insert_data_query2, data2_out)

        conn.commit()
        print(f"{cur.rowcount} Zeilen eingefügt.")

        # Daten abfragen
        print("Frage Beispieldaten ab...")

        # import query


        try: 
            yourinput = input("which function do you want to test\n")

        except e:
            print("no such query found")
        queryfile = open("queries.json", "r")

        query = json.loads(queryfile.read())[yourinput]["postgres"]
        queryfile.close()

        starttime = time.time_ns()
        cur.execute(query)
        endtime = time.time_ns()
        results = cur.fetchall()

        for row in results:
            print(row)

    except Exception as e:
        print(f"Fehler: {e}")

    finally:
        input("wait for input to close database")

        # Cursor und Verbindung schließen
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
            print("Verbindung zur PostgreSQL-Datenbank geschlossen.")

        # Container stoppen und löschen
        print("query execution time: " + str(endtime - starttime))
        print("Stoppe den Container...")
        try:
            container.stop()
            container.remove()
            print("Container stopped and deleted.")
        except Exception as e:
            print(f"Exception while stopping/deleting the container: {e}")

if __name__ == "__main__":
    manage_postgresql_with_docker()
