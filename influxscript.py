# imports
import docker
import time
import requests
import subprocess
import json

def flush_memory(token):
    """
    Dummy-Daten schreiben, um den WAL (Write-Ahead Log) zu leeren.
    """
    print("Flushe Speicher...")
    influxdb_url = "http://localhost:8086/api/v2/write"
    params = {
        "bucket": "example_bucket0",
        "org": "example_org",
        "precision": "s",
    }
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "text/plain",
    }
    
    dummy_data = "flush_measurement value=0"
    requests.post(influxdb_url, params=params, headers=headers, data=dummy_data)
    time.sleep(1)  # Kurze Pause, damit Daten persistiert werden

def preload_dummy_query(token):
    """
    Führt eine Dummy-Abfrage aus, um zwischengespeicherte Query-Ergebnisse zu entfernen.
    """
    print("Führe Dummy-Query aus, um Cache zu beeinflussen...")
    query_url = "http://localhost:8086/api/v2/query"
    query = '''
    from(bucket: "example_bucket0")
      |> range(start: -1m)
      |> limit(n: 1)
    '''
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/vnd.flux",
        "Accept": "application/csv"
    }
    requests.post(query_url, params={"org": "example_org"}, headers=headers, data=query)
    time.sleep(1)  # Sicherstellen, dass der Cache geleert wird


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
                "DOCKER_INFLUXDB_INIT_BUCKET": "example_bucket0",
            },
            detach=True,
        )
        print(f"InfluxDB-Container gestartet. Container-ID: {container.id}")

        # Wartezeit, bis der Container bereit ist
        time.sleep(5)

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
                token = line.split()[1]  # Token steht in der zweiten Spalte
                break

        if not token:
            print("Fehler: Konnte API-Token nicht extrahieren.")
            return

        print(f"API-Token: {token}")


        print("Rufe Org-ID ab...")
        org_url = "http://localhost:8086/api/v2/orgs"
        headers = {
            "Authorization": f"Token {token}",
            "Accept": "application/json"
        }

        org_response = requests.get(org_url, headers=headers)
        if org_response.status_code == 200:
            org_data = org_response.json()
            org_id = org_data["orgs"][0]["id"]  # Die erste Organisation nehmen
            print(f" Org-ID: {org_id}")
        else:
            print(f" Fehler beim Abrufen der Org-ID: {org_response.status_code}, {org_response.text}")
            return

        # **Zusätzliche Buckets erstellen**
        print("Erstelle zusätzliche Buckets...")
        influxdb_url = "http://localhost:8086/api/v2/buckets"

        buckets = ["example_bucket1", "example_bucket2"]

        for bucket in buckets:
            data = json.dumps({
                "orgID": org_id,  # **Hier verwenden wir die Org-ID**
                "name": bucket,
                "retentionRules": []
            })
            response = requests.post(influxdb_url, headers=headers, data=data)

            if response.status_code == 201:
                print(f"Bucket {bucket} erfolgreich erstellt.")
            else:
                print(f"Fehler beim Erstellen von {bucket}: {response.status_code}, {response.text}")


        # Daten in die Datenbank schreiben
        print("Schreibe Daten in die Datenbank...")
        influxdb_url = "http://localhost:8086/api/v2/write"
        params = {
            "bucket": "example_bucket0",
            "org": "example_org",
            "precision": "s",
        }
        headers = {
            "Authorization": f"Token {token}",
            "Content-Type": "text/plain",
        }

        f = open("influxdata0.txt","r")
        data = f.read().strip()
        f.close()

        response = requests.post(influxdb_url, params=params, headers=headers, data=data)

        if response.status_code == 204:
            print("Daten in example_bucket0 erfolgreich geschrieben.")
        else:
            print(f"Fehler beim Schreiben der Daten: {response.status_code}, {response.text}")

        
        params = {
            "bucket": "example_bucket1",
            "org": "example_org",
            "precision": "s",
        }
        f = open("influxdata1.txt","r")
        data = f.read().strip()
        f.close()

        response = requests.post(influxdb_url, params=params, headers=headers, data=data)

        if response.status_code == 204:
            print("Daten in example_bucket0 erfolgreich geschrieben.")
        else:
            print(f"Fehler beim Schreiben der Daten: {response.status_code}, {response.text}")

        params = {
            "bucket": "example_bucket2",
            "org": "example_org",
            "precision": "s",
        }
        f = open("influxdata2.txt","r")
        data = f.read().strip()
        f.close()

        response = requests.post(influxdb_url, params=params, headers=headers, data=data)

        if response.status_code == 204:
            print("Daten in example_bucket2 erfolgreich geschrieben.")
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

        try: 
            yourinput = input("which function do you want to test\n")

        except e:
            print("no such query found")
        with open("queries.json", "r") as queryfile:
            queries = json.load(queryfile)
            print(queries)
            logs = open("influxqueryresponses.txt", "a")
            for item in queries:

                print(item)
                query = queries[item]["influx"]
                #sumquery = json.loads(queryfile.read())["sum"]["influx"]
                print(query)

                headers.update({"Content-Type": "application/vnd.flux", "Accept": "application/csv"})

                flush_memory(token)
                # **Preload-Dummy-Query, um Cache-Effekte zu minimieren**
                preload_dummy_query(token)

                # Startzeit der Query Ausführung 
                starttime = time.time_ns()
                query_response = requests.post(query_url, params={"org": "example_org"}, headers=headers, data=query)

                endtime = time.time_ns()

                

                if query_response.status_code == 200:
                    print("Query erfolgreich ausgeführt. Ergebnisse:")
                    print(query_response.elapsed, query_response.text)
                    logs.write(str(query_response.elapsed) +" " +  str(item) + "\n" +  query_response.text)
                else:
                    print(f"Fehler bei der Query: {query_response.status_code}, {query_response.text}")

    except Exception as e:
        print(f"Fehler: {e}")

    finally:
        # Warte 20 Sekunden, bevor der Container gestoppt wird
        #print("Warte 20 Sekunden...")
        input("waiting for input to stop the program")

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
