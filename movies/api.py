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
        
        query = "SELECT m.id, m.title, m.year, m.director, m.runtime_minutes, m.genres FROM movie AS m"
        
        dbquery = cur.execute(query)
        row_headers=[x[0] for x in cur.description] 
        result = cur.fetchall()
        json_data=[]
        for r in result:
            json_data.append(dict(zip(row_headers,r)))
        print(jsonify(json_data), flush=True)  
        return jsonify({'movies': json_data})
        
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