# cinema_catalog Service

# Import framework
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import requests, psycopg2, json, os
from security import *

# Instantiate the app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
api = Api(app)

security_mode = os.getenv('SECURITYMODE')

@app.route('/venues')
def get_venues():
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")
    try:
        cur = conn.cursor()

        if security_mode == 'Decentralized':

            client_id = request.form.get("client_id")
            client_secret = request.form.get("client_secret")

            auth = authenticate(client_id, client_secret)

            if not auth:
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
                return jsonify({'success': False, 'details': f'Error while contacting security service. Status code: {r.status_code}'})

            data = json.loads(r.text)

            if not "clientId" in data:
                return jsonify({'success': False, 'details': f'Unauthorized to use this service.'}), 401
        
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

@app.route('/movies_cinema', methods=["POST"])
def get_movies_per_cinema():
    id_venue = request.form.get("id_venue")
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")
    try:
        cur = conn.cursor()

        if security_mode == 'Decentralized':

            client_id = request.form.get("client_id")
            client_secret = request.form.get("client_secret")

            auth = authenticate(client_id, client_secret)

            if not auth:
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
                return jsonify({'success': False, 'details': f'Error while contacting security service. Status code: {r.status_code}'})

            data = json.loads(r.text)

            if not "clientId" in data:
                return jsonify({'success': False, 'details': f'Unauthorized to use this service.'}), 401

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

@app.route('/movie_times_cinema', methods=["POST"])
def get_movie_times_per_cinema():
    id_movie_venue = request.form.get("id_movie_venue")
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")
    try:
        cur = conn.cursor()

        if security_mode == 'Decentralized':

            client_id = request.form.get("client_id")
            client_secret = request.form.get("client_secret")

            auth = authenticate(client_id, client_secret)

            if not auth:
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
                return jsonify({'success': False, 'details': f'Error while contacting security service. Status code: {r.status_code}'})

            data = json.loads(r.text)

            if not "clientId" in data:
                return jsonify({'success': False, 'details': f'Unauthorized to use this service.'}), 401

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

@app.route('/movie_seats_venue_times', methods=["POST"])
def get_movie_seats_per_venue_and_times():
    id_movie_time = request.form.get("id_movie_time")
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")
    try:
        cur = conn.cursor()

        if security_mode == 'Decentralized':

            client_id = request.form.get("client_id")
            client_secret = request.form.get("client_secret")

            auth = authenticate(client_id, client_secret)

            if not auth:
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
                return jsonify({'success': False, 'details': f'Error while contacting security service. Status code: {r.status_code}'})

            data = json.loads(r.text)

            if not "clientId" in data:
                return jsonify({'success': False, 'details': f'Unauthorized to use this service.'}), 401

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

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)