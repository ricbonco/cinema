# Reports Service

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

# Create routes
@app.route('/payments')
def get_payments():
    get_telemetry('payments_start')
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")
    try:
        cur = conn.cursor()

        get_telemetry('payments_security_start')
        if security_mode == 'Decentralized':

            client_id = request.form.get("client_id")
            client_secret = request.form.get("client_secret")

            auth = authenticate(client_id, client_secret)

            if not auth:
                get_telemetry('payments_security_end')
                return jsonify({'success': False, 'details': f'Unauthorized to use this service.'}), 401
            else:
                isAdmin = auth['isAdmin']
                isEmployee = auth['isEmployee']
            
        else:        
            authorizationHeader = request.headers.get('authorization')	

            header = {'Authorization': f'{authorizationHeader}'}

            url = "http://security-service/verify"
            r = requests.post(url, headers = header)

            data = json.loads(r.text)
            if "details" in data and data["details"] == "Token has expired":
                get_telemetry('movies_security_end')
                return jsonify({'success': False, 'details': f'Token has expired'}), 401

            if r.status_code != 200:
                get_telemetry('payments_security_end')
                return jsonify({'success': False, 'details': f'Error while contacting security service. Status code: {r.status_code}'})

            if not "clientId" in data:
                get_telemetry('payments_security_end')
                return jsonify({'success': False, 'details': f'Unauthorized to use this service.'}), 401

            isAdmin = data['isAdmin']
            isEmployee = data['isEmployee']

        if not isAdmin:
            get_telemetry('payments_security_end')
            return jsonify({'success': False, 'details': f'Unauthorized to use this service. Only admins can access this service.'}), 403

        get_telemetry('payments_security_end')

        query = """SELECT p.id AS id_payments, p.id_booking, p.approved, p.last_digits, p.time, p.username
                   FROM payment AS p"""
        
        dbquery = cur.execute(query)
        row_headers=[x[0] for x in cur.description] 
        result = cur.fetchall()
        json_data=[]
        for r in result:
            json_data.append(dict(zip(row_headers,r)))
        print(jsonify(json_data), flush=True)  
        return jsonify({'payments': json_data})
        
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
        get_telemetry('payments_end')

@app.route('/notifications')
def get_notifications():
    get_telemetry('notifications_start')
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")
    try:
        cur = conn.cursor()

        get_telemetry('notifications_security_start')
        if security_mode == 'Decentralized':

            client_id = request.form.get("client_id")
            client_secret = request.form.get("client_secret")

            auth = authenticate(client_id, client_secret)

            if not auth:
                get_telemetry('notifications_security_end')
                return jsonify({'success': False, 'details': f'Unauthorized to use this service.'}), 401
            else:
                isAdmin = auth['isAdmin']
                isEmployee = auth['isEmployee']
            
        else:        
            authorizationHeader = request.headers.get('authorization')	

            header = {'Authorization': f'{authorizationHeader}'}

            url = "http://security-service/verify"
            r = requests.post(url, headers = header)

            data = json.loads(r.text)
            if "details" in data and data["details"] == "Token has expired":
                get_telemetry('movies_security_end')
                return jsonify({'success': False, 'details': f'Token has expired'}), 401

            if r.status_code != 200:
                get_telemetry('notifications_security_end')
                return jsonify({'success': False, 'details': f'Error while contacting security service. Status code: {r.status_code}'})

            if not "clientId" in data:
                get_telemetry('notifications_security_end')
                return jsonify({'success': False, 'details': f'Unauthorized to use this service.'}), 401

            isAdmin = data['isAdmin']
            isEmployee = data['isEmployee']

        if not isAdmin and not isEmployee:
            get_telemetry('notifications_security_end')
            return jsonify({'success': False, 'details': f'Unauthorized to use this service. Only admins and employees can access this service.'}), 403

        get_telemetry('notifications_security_end')

        query = """SELECT n.id AS id_notification, n.sender, n.recipient, n.subject, n.body, n.time, n.username
                   FROM notification AS n"""
        
        dbquery = cur.execute(query)
        row_headers=[x[0] for x in cur.description] 
        result = cur.fetchall()
        json_data=[]
        for r in result:
            json_data.append(dict(zip(row_headers,r)))
        print(jsonify(json_data), flush=True)  
        return jsonify({'notification': json_data})
        
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
        get_telemetry('notifications_end')

def get_telemetry(operation):
    if telemetry:
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        log(f"{datetime.now()},{operation},{cpu_usage},{ram_usage}")

def log(text):
    file_name = "reports.csv"
    file = open(file_name, "a")  
    if os.path.getsize(file_name) == 0:
        file.write(f"Time,Operation,CPU,RAM\n") 
    file.write(f"{text}\n")
    file.close()   

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)