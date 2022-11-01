import os, shutil, requests, psutil, json, random
from datetime import datetime 

def run_movies_flow(cycles):
    print("Running 'run_movies_flow'")
    for i in range(cycles):
        get_telemetry('movies_flow_start')

        print(f"Cycle #{i}")

        # Calling movies
        print(" Running 'movies' service")  
        url = "http://localhost:8081/movies"
        body = {'client_id' : client_id, 'client_secret' : client_secret}
        r = requests.get(url, data = body, headers = header)
        print_response(url, r)

        get_telemetry('movies_flow_end')

def run_cinema_catalog_flow(cycles):    
    print("Running 'run_cinema_catalog_flow'")  
    for i in range(cycles):
        get_telemetry('cinema_catalog_flow_start')

        print(f"Cycle #{i}")

        # Calling venues
        print(" Running 'venues' service")  
        url = "http://localhost:8082/venues"
        body = {'client_id' : client_id, 'client_secret' : client_secret}
        r = requests.get(url, data = body, headers = header)
        print_response(url, r)
        data = json.loads(r.text)
        venues_count = len(data["venues"])
        index = random.randint(0, venues_count-1)
        id_venue = data["venues"][index]["id_venue"]

        # Calling movies_cinema
        print(" Running 'movies_cinema' service")  
        url = "http://localhost:8082/movies_cinema"
        body = {'client_id' : client_id, 'client_secret' : client_secret, 'id_venue' : id_venue}
        r = requests.post(url, data = body, headers = header)
        print_response(url, r)
        data = json.loads(r.text)
        movies_by_venues_count = len(data["movies_by_venues"])
        index = random.randint(0, movies_by_venues_count-1)
        id_movie_venue = data["movies_by_venues"][index]["id_movie_venue"]
        
        # Calling movie_times_cinema
        print(" Running 'movie_times_cinema' service")  
        url = "http://localhost:8082/movie_times_cinema"
        body = {'client_id' : client_id, 'client_secret' : client_secret, 'id_movie_venue' : id_movie_venue}
        r = requests.post(url, data = body, headers = header)
        print_response(url, r)
        data = json.loads(r.text)
        movie_times_cinema_count = len(data["movie_times_cinema"])
        index = random.randint(0, movie_times_cinema_count-1)
        id_movie_time = data["movie_times_cinema"][index]["id_movies_times"]

        # Calling movie_seats_venue_times
        print(" Running 'movie_seats_venue_times' service")  
        url = "http://localhost:8082/movie_seats_venue_times"
        body = {'client_id' : client_id, 'client_secret' : client_secret, 'id_movie_time' : id_movie_time}
        r = requests.post(url, data = body, headers = header)
        print_response(url, r)
        data = json.loads(r.text)
        
        get_telemetry('cinema_catalog_flow_end')

def copy_logs():
    now = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
    logs_directory = f"logs/{now}"
    if not os.path.isdir("logs"):
        os.mkdir("logs")
    os.mkdir(logs_directory)
    if os.path.exists("log.csv"):
        shutil.move("log.csv", f"{logs_directory}/log.csv")
    if os.path.exists("movies/movies.csv"):
        shutil.move("movies/movies.csv", f"{logs_directory}/movies.csv")
    if os.path.exists("cinema_catalog/cinema_catalog.csv"):        
        shutil.move("cinema_catalog/cinema_catalog.csv", f"{logs_directory}/cinema_catalog.csv")
    

def print_response(url, response):
    print(f"  URL: {url}\n    Status Code: {response.status_code}\n      Output: {response.text}")

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
    print_response(url, r)
    data = json.loads(r.text)
    if "token" in data:
        return data["token"]
    else:
        print(f"Error when authenticating '{client_id}'")
        return False

def set_up(print_telemetry, user_id, user_password):
    global telemetry, client_id, client_secret, header

    telemetry = print_telemetry
    client_id = user_id
    client_secret = user_password

    token = authenticate(client_id, client_secret)

    header = {'Authorization': f'Bearer {token}'}

def main():
    
    set_up(True, 'ricardo', 'ricardo1234')

    get_telemetry('test_start')

    run_movies_flow(5)
    run_cinema_catalog_flow(5)

    get_telemetry('test_end')

    copy_logs()

if __name__ == "__main__":
    main()