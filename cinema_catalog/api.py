# Movies Service

# Import framework
from flask import Flask, jsonify
from flask_restful import Resource, Api
import requests, psycopg2

# Instantiate the app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
api = Api(app)

def get_cinemas():
    return ['Cinemark', 'Nova', 
            'CCM',
            'Cinepolis']

@app.route('/movies_cinema')
def get_movies_per_cinema():
    r = requests.get('http://movies-service/movies')
    movies = r.json()

    movies_per_cinema = {}
    for cinema in get_cinemas():
        movies_per_cinema[cinema] = movies

    return jsonify(movies_per_cinema)

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)