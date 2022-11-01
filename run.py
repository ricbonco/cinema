import os, shutil, requests, psutil, json
from datetime import datetime 

def run_movies_flow(cycles):
    print("Running 'run_movies_flow'")
    for i in range(cycles):
        get_telemetry('movies_start')

        url = "http://localhost:8081/movies"
        body = {'client_id' : client_id, 'client_secret' : client_secret}
        r = requests.get(url, data = body, headers = header)
        print_response(r)

        get_telemetry('movies_end')

def run_cinema_catalog_flow(cycles):    
    print("Running 'run_cinema_catalog_flow'")  
    for i in range(cycles):
        get_telemetry('venues_start')

        url = "http://localhost:8082/venues"
        body = {'client_id' : client_id, 'client_secret' : client_secret}
        r = requests.get(url, data = body, headers = header)
        print_response(r)

        get_telemetry('venues_end')

def copy_logs():
    now = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
    logs_directory = f"logs/{now}"
    if not os.path.isdir("logs"):
        os.mkdir("logs")
    os.mkdir(logs_directory)
    if os.path.exists("log.csv"):
        shutil.move("log.csv", f"{logs_directory}/log.csv")
    shutil.move("movies/movies.csv", f"{logs_directory}/movies.csv")

def print_response(response):
    print(f"  Status Code: {response.status_code}\n    Output: {response.text}")

def get_telemetry(operation):
    if telemetry:
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        log(f"{datetime.now()},{operation},{cpu_usage},{ram_usage}")

def log(text):
    if telemetry:
        file = open("log.csv", "a")  
        file.write(f"{text}\n")
        file.close()   

def authenticate(client_id, client_secret):
    url = "http://localhost:8080/auth"
    body = {'client_id' : client_id, 'client_secret' : client_secret}
    r = requests.post(url, data = body)
    print_response(r)
    data = json.loads(r.text)
    if "token" in data:
        return data["token"]
    else:
        print(f"Error when authenticating '{client_id}'")
        return False

def set_up():
    global telemetry, client_id, client_secret, header

    telemetry = True
    client_id = 'ricardo'
    client_secret = 'ricardo1234'

    token = authenticate(client_id, client_secret)

    header = {'Authorization': f'Bearer {token}'}

def main():
    
    set_up()

    get_telemetry('test_start')

    run_movies_flow(5)
    run_cinema_catalog_flow(5)

    get_telemetry('test_end')

    copy_logs()

if __name__ == "__main__":
    main()