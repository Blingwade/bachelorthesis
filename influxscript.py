# imports
import docker
import time
import requests
import subprocess
import json

def manage_influxdb():
    # Docker-Client initialisieren
    client = docker.from_env()

    try:
        # InfluxDB-Container starten
        print("Starte InfluxDB-Container...")
        container = client.containers.run(
            image="influxdb:latest",
            name="influxdb-container",
            ports={"8086/tcp": 8086},
            environment={
                "DOCKER_INFLUXDB_INIT_MODE": "setup",
                "DOCKER_INFLUXDB_INIT_USERNAME": "admin",
                "DOCKER_INFLUXDB_INIT_PASSWORD": "password",
                "DOCKER_INFLUXDB_INIT_ORG": "example_org",
                "DOCKER_INFLUXDB_INIT_BUCKET": "example_bucket",
            },
            detach=True,
        )
        print(f"InfluxDB-Container gestartet. Container-ID: {container.id}")

        # Wartezeit, bis der Container bereit ist
        time.sleep(10)

        # API-Token erstellen
        print("Erstelle API-Token...")
        create_token_command = [
            "docker", "exec", "-i", "influxdb-container",
            "influx", "auth", "create",
            "--all-access",
            "--user", "admin"
        ]
        result = subprocess.run(create_token_command, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Fehler beim Erstellen des API-Tokens: {result.stderr}")
            return

        # Debug-Ausgabe, um die komplette Ausgabe des Befehls zu sehen
        print(f"Ausgabe von 'influx auth create':\n{result.stdout}")

        # Extrahiere Token aus der Ausgabe
        token = None
        for line in result.stdout.split("\n"):
            if "admin" in line and len(line.split()) > 2:
                token = line.split()[1]  # Token steht in der dritten Spalte
                break

        if not token:
            print("Fehler: Konnte API-Token nicht extrahieren.")
            return

        print(f"API-Token: {token}")

        # Daten in die Datenbank schreiben
        print("Schreibe Daten in die Datenbank...")
        influxdb_url = "http://localhost:8086/api/v2/write"
        params = {
            "bucket": "example_bucket",
            "org": "example_org",
            "precision": "s",
        }
        headers = {
            "Authorization": f"Token {token}",
            "Content-Type": "text/plain",
        }

        f = open("data.txt","r")
        data = f.read().strip()
        #print(data)
        f.close()

        response = requests.post(influxdb_url, params=params, headers=headers, data=data)

        if response.status_code == 204:
            print("Daten erfolgreich geschrieben.")
        else:
            print(f"Fehler beim Schreiben der Daten: {response.status_code}, {response.text}")

        
        # Query ausführen
        print("Führe Query aus, um alle homes abzurufen...")
        query_url = "http://localhost:8086/api/v2/query"
        #query = '''
        #from(bucket: "example_bucket")
        #  |> range(start: 0)
        #  |> filter(fn: (r) => r._measurement == "home")
        #'''
        queryfile = open("queries.json", "r")
        
        query = json.loads(queryfile.read())["example"]["influx"]

        print(query)

        headers.update({"Content-Type": "application/vnd.flux", "Accept": "application/csv"})


        # Startzeit der Query Ausführung 
        starttime = time.time_ns()

        query_response = requests.post(query_url, params={"org": "example_org"}, headers=headers, data=query)

        endtime = time.time_ns()

        if query_response.status_code == 200:
            print("Query erfolgreich ausgeführt. Ergebnisse:")
            print(query_response.elapsed, query_response.text)
        else:
            print(f"Fehler bei der Query: {query_response.status_code}, {query_response.text}")

    except Exception as e:
        print(f"Fehler: {e}")

    finally:
        # Warte 20 Sekunden, bevor der Container gestoppt wird
        #print("Warte 20 Sekunden...")
        time.sleep(10)

        # Container stoppen und löschen
        print("Stoppe den Container...")
        try:
            container.stop()
            container.remove()
            print("Container erfolgreich gestoppt und gelöscht.")
            print("Laufzeit der Query: " + str(endtime - starttime))

        except Exception as e:
            print(f"Fehler beim Stoppen/Löschen des Containers: {e}")

if __name__ == "__main__":
    manage_influxdb()
