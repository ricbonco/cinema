# Movies Service

# Import framework
from flask import Flask, jsonify
from flask_restful import Resource, Api
import requests, psycopg2

# Instantiate the app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
api = Api(app)

# Create routes
@app.route('/movies')
def get_movies():
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")
    try:
        cur = conn.cursor()
        dbquery = cur.execute("SELECT * FROM movies")
        result = cur.fetchall()
        return jsonify({'movies': result})
        
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