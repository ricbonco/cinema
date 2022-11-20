# Movies Service

# Import framework
from urllib import response
from flask import Flask, request, jsonify, Response
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

# Create routes
@app.route('/movies')
def get_movies():
    get_telemetry('movies_start')
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")
    try:
        cur = conn.cursor()

        get_telemetry('movies_security_start')
        if security_mode == 'Decentralized':

            client_id = request.form.get("client_id")
            client_secret = request.form.get("client_secret")

            auth = authenticate(client_id, client_secret)

            if not auth:
                get_telemetry('movies_security_end')
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
                get_telemetry('movies_security_end')
                return jsonify({'success': False, 'details': f'Error while contacting security service. Status code: {r.status_code}'})
 
            data = json.loads(r.text)

            if not "clientId" in data:
                get_telemetry('movies_security_end')
                return jsonify({'success': False, 'details': f'Unauthorized to use this service.'}), 401
            
            isAdmin = data['isAdmin']
            isEmployee = data['isEmployee']

        if not isAdmin and not isEmployee:
            get_telemetry('movies_security_end')
            return jsonify({'success': False, 'details': f'Unauthorized to use this service. Only admins or employees can access this service.'}), 401

        get_telemetry('movies_security_end')

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
        get_telemetry('movies_end')
        

def get_telemetry(operation):
    if telemetry:
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        log(f"{datetime.now()},{operation},{cpu_usage},{ram_usage}")

def log(text):
    file_name = "movies.csv"
    file = open(file_name, "a")  
    if os.path.getsize(file_name) == 0:
        file.write(f"Time,Operation,CPU,RAM\n") 
    file.write(f"{text}\n")
    file.close()             
    
# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)