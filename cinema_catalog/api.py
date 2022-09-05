# cinema_catalog Service

# Import framework
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import requests, psycopg2

# Instantiate the app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
api = Api(app)

@app.route('/venues')
def get_venues():
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")
    try:
        cur = conn.cursor()
        
        query = "SELECT v.id as id_venue, v.name, v.location FROM venues AS v"

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

        query = f"""SELECT mv.id as id_movie_venue, m.id as id_movie, m.title, v.id as id_venue, CONCAT(v.name, ' ', v.location) as venue_name
                    FROM movies_venues AS mv
                    INNER JOIN venues AS v
                    ON v.id = mv.id_venue
                    AND mv.id_venue = {id_venue}
                    INNER JOIN movies AS m
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
    id_movies_venue = request.form.get("id_movies_venue")
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")
    try:
        cur = conn.cursor()

        query = f"""SELECT mt.id as id_movies_times, m.title, CONCAT(v.name, ' ', v.location) as venue, mt.movie_date
                   FROM movies_times as mt
                   INNER JOIN movies_venues as mv
                     ON mv.id = mt.id_movies_venues
                      AND mt.id_movies_venues = {id_movies_venue}
                   INNER JOIN venues AS v
                    ON v.id = mv.id_venue
                   INNER JOIN movies AS m
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
    id_movies_times = request.form.get("id_movies_times")
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")
    try:
        cur = conn.cursor()

        query = f"""SELECT ms.id as id_movies_seats, ms.id_seat_type, m.title, CONCAT(v.name, ' ', v.location) as venue, ms.total_seats, ms.available_seats, ms.price::numeric::float, cv.catalog_value as ticket_type 
                   FROM movies_seats as ms
                   INNER JOIN movies_times as mt
                     ON mt.id = ms.id_movies_times
                       AND ms.id_movies_times = {id_movies_times}
                   INNER JOIN catalogs_values as cv
                    ON cv.id = ms.id_seat_type
                   INNER JOIN movies_venues as mv
                     ON mv.id = mt.id_movies_venues
                   INNER JOIN venues AS v
                    ON v.id = mv.id_venue
                   INNER JOIN movies AS m
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