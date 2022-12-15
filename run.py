import os, shutil, requests, psutil, json, random, pandas as pd
from datetime import datetime 

def run_movies_flow(cycles):
    print("Running 'run_movies_flow'")
    for i in range(cycles):
        get_telemetry('movies_flow_start')

        print(f" Cycle #{i}")

        # Calling movies
        print("  Running 'movies' service")  
        url = "http://localhost:8081/movies"
        body = {'client_id' : client_id, 'client_secret' : client_secret}
        r = requests.get(url, data = body, headers = header)
        print_response(url, r)

        get_telemetry('movies_flow_end')

def run_cinema_catalog_flow(cycles):    
    print("Running 'run_cinema_catalog_flow'")  
    potential_bookings = []
    for i in range(cycles):
        get_telemetry('cinema_catalog_flow_start')

        print(f" Cycle #{i}")

        # Calling venues
        print("  Running 'venues' service")  
        url = "http://localhost:8082/venues"
        body = {'client_id' : client_id, 'client_secret' : client_secret}
        r = requests.get(url, data = body, headers = header)
        print_response(url, r)
        data = json.loads(r.text)
        venues_count = len(data["venues"])
        index = random.randint(0, venues_count-1)
        id_venue = data["venues"][index]["id_venue"]

        # Calling movies_cinema
        print("  Running 'movies_cinema' service")  
        url = "http://localhost:8082/movies_cinema"
        body = {'client_id' : client_id, 'client_secret' : client_secret, 'id_venue' : id_venue}
        r = requests.post(url, data = body, headers = header)
        print_response(url, r)
        data = json.loads(r.text)
        movies_by_venues_count = len(data["movies_by_venues"])
        index = random.randint(0, movies_by_venues_count-1)
        id_movie_venue = data["movies_by_venues"][index]["id_movie_venue"]
        
        # Calling movie_times_cinema
        print("  Running 'movie_times_cinema' service")  
        url = "http://localhost:8082/movie_times_cinema"
        body = {'client_id' : client_id, 'client_secret' : client_secret, 'id_movie_venue' : id_movie_venue}
        r = requests.post(url, data = body, headers = header)
        print_response(url, r)
        data = json.loads(r.text)
        movie_times_cinema_count = len(data["movie_times_cinema"])
        index = random.randint(0, movie_times_cinema_count-1)
        id_movie_time = data["movie_times_cinema"][index]["id_movies_times"]

        # Calling movie_seats_venue_times
        print("  Running 'movie_seats_venue_times' service")  
        url = "http://localhost:8082/movie_seats_venue_times"
        body = {'client_id' : client_id, 'client_secret' : client_secret, 'id_movie_time' : id_movie_time}
        r = requests.post(url, data = body, headers = header)
        print_response(url, r)
        data = json.loads(r.text)
        movie_seats_venue_times_count = len(data["movie_seats_venue_times"])
        index = random.randint(0, movie_seats_venue_times_count-1)
        id_seat_type = data["movie_seats_venue_times"][index]["id_seat_type"]
        
        potential_bookings.append({'id_movie_time' : id_movie_time, 'id_seat_type': id_seat_type})

        get_telemetry('cinema_catalog_flow_end')

    return potential_bookings

def run_bookings_flow(potential_bookings):    
    print("Running 'run_bookings_flow'") 
    actual_bookings = [] 
    for i in range(len(potential_bookings)):
        get_telemetry('bookings_flow_start')

        data = potential_bookings[i]

        id_movie_time = data["id_movie_time"]
        id_seat_type = data["id_seat_type"]
        requested_seats = random.randint(1, 4)

        print(f" Cycle #{i}")

        # Calling bookings service
        print("  Running 'bookings' service")  
        url = "http://localhost:8083/book"
        body = {'client_id' : client_id, 'client_secret' : client_secret, 'id_movie_time': id_movie_time, 
                'id_seat_type' : id_seat_type, 'requested_seats': requested_seats}
        r = requests.post(url, data = body, headers = header)
        print_response(url, r)
        data = json.loads(r.text)

        if "success" not in data:
            actual_bookings.append(data["id_booking"])
        
        get_telemetry('bookings_flow_end')

    return actual_bookings

def run_payments_flow(actual_bookings):    
    print("Running 'run_payments_flow'") 
    for i in range(len(actual_bookings)):
        get_telemetry('payments_flow_start')

        id_booking = actual_bookings[i]

        print(f" Cycle #{i}")

        # Calling subtotal
        print("  Running 'subtotal' service")  
        url = "http://localhost:8084/subtotal"
        body = {'client_id' : client_id, 'client_secret' : client_secret, 'id_booking': id_booking}
        r = requests.get(url, data = body, headers = header)
        print_response(url, r)

        # Calling pay
        print("  Running 'pay' service")  
        url = "http://localhost:8084/pay"
        card_number = f'377{random.randint(700000000000, 799999999999)}'
        expiration_date = f'{random.randint(1, 12):02d}/{random.randint(24, 30)}'
        card_verification_value = f'{random.randint(0000, 9999):04d}'
        body = {'client_id' : client_id, 'client_secret' : client_secret, 'id_booking': id_booking, 
                'card_number' : card_number, 
                'expiration_date': expiration_date, 
                'card_verification_value' : card_verification_value}
        r = requests.post(url, data = body, headers = header)
        print_response(url, r)
        data = json.loads(r.text)
        
        get_telemetry('payments_flow_end')

def run_reports_flow(cycles):
    print("Running 'run_reports_flow'")
    for i in range(cycles):
        get_telemetry('reports_flow_start')

        print(f" Cycle #{i}")

        # Calling payments
        print("  Running 'payments' service")  
        url = "http://localhost:8086/payments"
        body = {'client_id' : client_id, 'client_secret' : client_secret}
        r = requests.get(url, data = body, headers = header)
        print_response(url, r)

        # Calling notifications
        print("  Running 'notifications' service")  
        url = "http://localhost:8086/notifications"
        body = {'client_id' : client_id, 'client_secret' : client_secret}
        r = requests.get(url, data = body, headers = header)
        print_response(url, r)

        get_telemetry('reports_flow_end')        

def convert_csv_to_xlsx(csv_location, xlsx_location):
    read_file = pd.read_csv (csv_location)
    read_file.to_excel (xlsx_location, index = None, header=True)

def copy_logs():
    print("Copying and converting logs")    
    now = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
    logs_directory = f"logs/{now}"
    if not os.path.isdir("logs"):
        os.mkdir("logs")
    os.mkdir(logs_directory)
    if os.path.exists("log.csv"):
        convert_csv_to_xlsx("log.csv", f"{logs_directory}/log.xlsx")
        shutil.move("log.csv", f"{logs_directory}/log.csv")
    if os.path.exists("movies/movies.csv"):
        convert_csv_to_xlsx("movies/movies.csv", f"{logs_directory}/movies.xlsx")
        shutil.move("movies/movies.csv", f"{logs_directory}/movies.csv")
    if os.path.exists("cinema_catalog/cinema_catalog.csv"):        
        convert_csv_to_xlsx("cinema_catalog/cinema_catalog.csv", f"{logs_directory}/cinema_catalog.xlsx")
        shutil.move("cinema_catalog/cinema_catalog.csv", f"{logs_directory}/cinema_catalog.csv")
    if os.path.exists("bookings/bookings.csv"):        
        convert_csv_to_xlsx("bookings/bookings.csv", f"{logs_directory}/bookings.xlsx")
        shutil.move("bookings/bookings.csv", f"{logs_directory}/bookings.csv")
    if os.path.exists("payments/payments.csv"):
        convert_csv_to_xlsx("payments/payments.csv", f"{logs_directory}/payments.xlsx")
        shutil.move("payments/payments.csv", f"{logs_directory}/payments.csv")
    if os.path.exists("notifications/notifications.csv"):
        convert_csv_to_xlsx("notifications/notifications.csv", f"{logs_directory}/notifications.xlsx")
        shutil.move("notifications/notifications.csv", f"{logs_directory}/notifications.csv")
    if os.path.exists("reports/reports.csv"):
        convert_csv_to_xlsx("reports/reports.csv", f"{logs_directory}/reports.xlsx")
        shutil.move("reports/reports.csv", f"{logs_directory}/reports.csv")

def print_response(url, response):
    print(f"   URL: {url}\n     Status Code: {response.status_code}\n       Output: {response.text}")

def get_telemetry(operation):
    if telemetry:
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        log(f"{datetime.now()},{operation},{cpu_usage},{ram_usage}")

def log(text):
    if telemetry:
        file_name = "log.csv"
        file = open(file_name, "a")  
        if os.path.getsize(file_name) == 0:
            file.write(f"Time,Operation,CPU,RAM\n") 
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

def bulk_flow(cycles):
    print("Running '*bulk_flow*'")

    set_up(True, 'cinemaadmin', '@dm1nP@$$w0rd')

    get_telemetry('test_start')

    run_movies_flow(cycles)
    potential_bookings = run_cinema_catalog_flow(cycles)
    actual_bookings = run_bookings_flow(potential_bookings)
    run_payments_flow(actual_bookings)
    run_reports_flow(cycles)

    get_telemetry('test_end')

def single_flow(cycles):
    print("Running '*single_flow*'")

    for i in range(cycles):

        set_up(True, 'cinemaadmin', '@dm1nP@$$w0rd')

        get_telemetry('test_start')    

        run_movies_flow(1)
        potential_bookings = run_cinema_catalog_flow(1)
        actual_bookings = run_bookings_flow(potential_bookings)
        run_payments_flow(actual_bookings)
        run_reports_flow(1)

        get_telemetry('test_end')  

def mixed_credentials_flow(cycles):
    print("Running '*mixed_credentials_flow*'")

    print("Logging as 'Cinema Admin'")
    set_up(True, 'cinemaadmin', '@dm1nP@$$w0rd')

    for i in range(cycles):

        get_telemetry('test_start')

        run_movies_flow(1)
        run_reports_flow(1)

        print("Logging as 'Cinema Employee'")
        set_up(True, 'cinemaemployee', '3mpl0y33P@$$w0rd')

        run_movies_flow(1)
        run_reports_flow(1)

        print("Logging as 'Cinema Customer'")
        set_up(True, 'cinemacustomer', 'cu$t0m3rP@$$w0rd')

        run_movies_flow(1)
        run_reports_flow(1)

        get_telemetry('test_end')  

def main():
    
    print(f'*** Date & Time: {datetime.now().strftime("%Y-%m-%d %H.%M.%S")} ***')
    bulk_flow(100)
    single_flow(100)
    mixed_credentials_flow(100)
    copy_logs()  

if __name__ == "__main__":
    main()
    