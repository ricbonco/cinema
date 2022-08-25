# cinema_catalog Service

# Import framework
from flask import Flask, jsonify
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
        dbquery = cur.execute("SELECT * FROM venues")
        result = cur.fetchall()
        print(jsonify(result), flush=True)  
        return jsonify({'venues': result})
        
    except (Exception, psycopg2.DatabaseError) as error:
        
        print(error, flush=True)
        if conn is not None:
            cur.close()
            conn.close()

        return False
    finally:
        if conn is not None:
            cur.close()
            conn.close()

@app.route('/movies_cinema')
def get_movies_per_cinema():
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")
    try:
        cur = conn.cursor()
        dbquery = cur.execute("""SELECT mv.id, m.id, m.title, v.id, CONCAT(v.name, ' ', v.location) FROM movies_venues AS mv
                                INNER JOIN movies AS m
                                ON m.id = mv.movie_id
                                INNER JOIN venues AS v
                                ON v.id = mv.venue_id""")
        result = cur.fetchall()
        print(jsonify(result), flush=True)  
        return jsonify({'movies_by_venues': result})
        
    except (Exception, psycopg2.DatabaseError) as error:
        
        print(error, flush=True)
        if conn is not None:
            cur.close()
            conn.close()

        return False
    finally:
        if conn is not None:
            cur.close()
            conn.close()

    
    
    #r = requests.get('http://movies-service/movies')
    #movies = r.json()
    #movies_per_cinema = {}
    #for cinema in get_cinemas():
    #    movies_per_cinema[cinema] = movies

    #print(movies_per_cinema, flush=True)  

    #return jsonify(movies_per_cinema)

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)