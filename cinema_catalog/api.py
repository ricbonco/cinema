# cinema_catalog Service

# Import framework
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import requests, psycopg2, json, os, psutil
from security import *
from datetime import datetime

# Instantiate the app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
api = Api(app)

security_mode = os.getenv('SECURITYMODE')
telemetry = os.getenv('TELEMETRY') == 'On'

@app.route('/venues')
def get_venues():
    get_telemetry('venues_start')
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")
    try:
        cur = conn.cursor()

        get_telemetry('venues_security_start')
        if security_mode == 'Decentralized':

            client_id = request.form.get("client_id")
            client_secret = request.form.get("client_secret")

            auth = authenticate(client_id, client_secret)

            if not auth:
                get_telemetry('venues_security_end')
                return jsonify({'success': False, 'details': f'Unauthorized to use this service.'}), 401
            else:
                isAdmin = auth['isAdmin']
                isEmployee = auth['isEmployee']
            
        else:        
            authorizationHeader = request.headers.get('authorization')	

            header = {'Authorization': f'{authorizationHeader}'}

            url = "http://security-service/verify"
            r = requests.post(url, headers = header)

            if r.status_code != 200:
                get_telemetry('venues_security_end')
                return jsonify({'success': False, 'details': f'Error while contacting security service. Status code: {r.status_code}'})

            data = json.loads(r.text)

            if not "clientId" in data:
                get_telemetry('venues_security_end')
                return jsonify({'success': False, 'details': f'Unauthorized to use this service.'}), 401

            isAdmin = data['isAdmin']
            isEmployee = data['isEmployee']
        get_telemetry('venues_security_end')
        
        query = "SELECT v.id as id_venue, v.name, v.location FROM venue AS v"

        dbquery = cur.execute(query)
        row_headers=[x[0] for x in cur.description] 
        result = cur.fetchall()
        json_data=[]
        for r in result:
            json_data.append(dict(zip(row_headers,r)))
        print(jsonify(json_data), flush=True)  
        return jsonify({'venues': json_data})
        
    except (Exception, psycopg2.DatabaseError) as error:
        
        print(error, flush=True)
        if conn is not None:
            cur.close()
            conn.close()

        return jsonify({'success': False})
    finally:
        if conn is not None:
            cur.close()
            conn.close()
        get_telemetry('venues_end')

@app.route('/movies_cinema', methods=["POST"])
def get_movies_per_cinema():
    get_telemetry('movies_cinema_start')
    id_venue = request.form.get("id_venue")
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")
    try:
        cur = conn.cursor()

        get_telemetry('movies_cinema_security_start')
        if security_mode == 'Decentralized':

            client_id = request.form.get("client_id")
            client_secret = request.form.get("client_secret")

            auth = authenticate(client_id, client_secret)

            if not auth:
                get_telemetry('movies_cinema_security_end')
                return jsonify({'success': False, 'details': f'Unauthorized to use this service.'}), 401
            else:
                isAdmin = auth['isAdmin']
                isEmployee = auth['isEmployee']
            
        else:        
            authorizationHeader = request.headers.get('authorization')	

            header = {'Authorization': f'{authorizationHeader}'}

            url = "http://security-service/verify"
            r = requests.post(url, headers = header)

            if r.status_code != 200:
                get_telemetry('movies_cinema_security_end')
                return jsonify({'success': False, 'details': f'Error while contacting security service. Status code: {r.status_code}'})

            data = json.loads(r.text)

            if not "clientId" in data:
                get_telemetry('movies_cinema_security_end')
                return jsonify({'success': False, 'details': f'Unauthorized to use this service.'}), 401

            isAdmin = data['isAdmin']
            isEmployee = data['isEmployee']
        get_telemetry('movies_cinema_security_end')

        query = f"""SELECT mv.id as id_movie_venue, m.id as id_movie, m.title, v.id as id_venue, CONCAT(v.name, ' ', v.location) as venue_name
                    FROM movie_venue AS mv
                    INNER JOIN venue AS v
                    ON v.id = mv.id_venue
                    AND mv.id_venue = {id_venue}
                    INNER JOIN movie AS m
                    ON m.id = mv.id_movie""" 

        dbquery = cur.execute(query)
        row_headers=[x[0] for x in cur.description] 
        result = cur.fetchall()
        json_data=[]
        for r in result:
            json_data.append(dict(zip(row_headers,r)))
        print(jsonify(json_data), flush=True)  
        return jsonify({'movies_by_venues': json_data})
        
    except (Exception, psycopg2.DatabaseError) as error:
        
        print(error, flush=True)
        if conn is not None:
            cur.close()
            conn.close()

        return jsonify({'success': False})
    finally:
        if conn is not None:
            cur.close()
            conn.close()
        get_telemetry('movies_cinema_end')

@app.route('/movie_times_cinema', methods=["POST"])
def get_movie_times_per_cinema():
    get_telemetry('movie_times_cinema_start')
    id_movie_venue = request.form.get("id_movie_venue")
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")
    try:
        cur = conn.cursor()

        get_telemetry('movie_times_cinema_security_start')
        if security_mode == 'Decentralized':

            client_id = request.form.get("client_id")
            client_secret = request.form.get("client_secret")

            auth = authenticate(client_id, client_secret)

            if not auth:
                get_telemetry('movie_times_cinema_security_end')
                return jsonify({'success': False, 'details': f'Unauthorized to use this service.'}), 401
            else:
                isAdmin = auth['isAdmin']
                isEmployee = auth['isEmployee']
            
        else:        
            authorizationHeader = request.headers.get('authorization')	

            header = {'Authorization': f'{authorizationHeader}'}

            url = "http://security-service/verify"
            r = requests.post(url, headers = header)

            if r.status_code != 200:
                get_telemetry('movie_times_cinema_security_end')
                return jsonify({'success': False, 'details': f'Error while contacting security service. Status code: {r.status_code}'})

            data = json.loads(r.text)

            if not "clientId" in data:
                get_telemetry('movie_times_cinema_security_end')
                return jsonify({'success': False, 'details': f'Unauthorized to use this service.'}), 401

            isAdmin = data['isAdmin']
            isEmployee = data['isEmployee']
        get_telemetry('movie_times_cinema_security_end')

        query = f"""SELECT mt.id as id_movies_times, m.title, CONCAT(v.name, ' ', v.location) as venue, mt.movie_date
                   FROM movie_time as mt
                   INNER JOIN movie_venue as mv
                     ON mv.id = mt.id_movie_venue
                      AND mt.id_movie_venue = {id_movie_venue}
                   INNER JOIN venue AS v
                    ON v.id = mv.id_venue
                   INNER JOIN movie AS m
                    ON m.id = mv.id_movie"""

        dbquery = cur.execute(query)
        row_headers=[x[0] for x in cur.description] 
        result = cur.fetchall()
        json_data=[]
        for r in result:
            json_data.append(dict(zip(row_headers,r)))
        print(jsonify(json_data), flush=True)  
        return jsonify({'movie_times_cinema': json_data})
        
    except (Exception, psycopg2.DatabaseError) as error:
        
        print(error, flush=True)
        if conn is not None:
            cur.close()
            conn.close()

        return jsonify({'success': False})
    finally:
        if conn is not None:
            cur.close()
            conn.close()
        get_telemetry('movie_times_cinema_end')

@app.route('/movie_seats_venue_times', methods=["POST"])
def get_movie_seats_per_venue_and_times():
    get_telemetry('movie_seats_venue_times_start')
    id_movie_time = request.form.get("id_movie_time")
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")
    try:
        cur = conn.cursor()

        get_telemetry('movie_seats_venue_times_security_start')
        if security_mode == 'Decentralized':

            client_id = request.form.get("client_id")
            client_secret = request.form.get("client_secret")

            auth = authenticate(client_id, client_secret)

            if not auth:
                get_telemetry('movie_seats_venue_times_security_end')
                return jsonify({'success': False, 'details': f'Unauthorized to use this service.'}), 401
            else:
                isAdmin = auth['isAdmin']
                isEmployee = auth['isEmployee']
            
        else:        
            authorizationHeader = request.headers.get('authorization')	

            header = {'Authorization': f'{authorizationHeader}'}

            url = "http://security-service/verify"
            r = requests.post(url, headers = header)

            if r.status_code != 200:
                get_telemetry('movie_seats_venue_times_security_end')
                return jsonify({'success': False, 'details': f'Error while contacting security service. Status code: {r.status_code}'})

            data = json.loads(r.text)

            if not "clientId" in data:
                get_telemetry('movie_seats_venue_times_security_end')
                return jsonify({'success': False, 'details': f'Unauthorized to use this service.'}), 401

            isAdmin = data['isAdmin']
            isEmployee = data['isEmployee']
        get_telemetry('movie_seats_venue_times_security_end')

        query = f"""SELECT ms.id as id_movie_seat, ms.id_seat_type, m.title, CONCAT(v.name, ' ', v.location) as venue, ms.total_seats, ms.available_seats, ms.price::numeric::float, cv.value as ticket_type 
                   FROM movie_seat as ms
                   INNER JOIN movie_time as mt
                     ON mt.id = ms.id_movie_time
                       AND ms.id_movie_time = {id_movie_time}
                   INNER JOIN catalog_value as cv
                    ON cv.id = ms.id_seat_type
                   INNER JOIN movie_venue as mv
                     ON mv.id = mt.id_movie_venue
                   INNER JOIN venue AS v
                    ON v.id = mv.id_venue
                   INNER JOIN movie AS m
                    ON m.id = mv.id_movie"""

        dbquery = cur.execute(query)
        row_headers=[x[0] for x in cur.description] 
        result = cur.fetchall()
        json_data=[]
        for r in result:
            json_data.append(dict(zip(row_headers,r)))
        print(jsonify(json_data), flush=True)  
        return jsonify({'movie_seats_venue_times': json_data})
        
    except (Exception, psycopg2.DatabaseError) as error:
        
        print(error, flush=True)
        if conn is not None:
            cur.close()
            conn.close()

        return jsonify({'success': False})
    finally:
        if conn is not None:
            cur.close()
            conn.close()
        get_telemetry('movie_seats_venue_times_end')

def get_telemetry(operation):
    if telemetry:
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        log(f"{datetime.now()},{operation},{cpu_usage},{ram_usage}")

def log(text):
    file_name = "cinema_catalog.csv"
    file = open(file_name, "a")  
    if os.path.getsize(file_name) == 0:
        file.write(f"Time,Operation,CPU,RAM\n")  
    file.write(f"{text}\n")
    file.close()   

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)