# Reports Service

# Import framework
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import requests, psycopg2, json

# Instantiate the app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
api = Api(app)

# Create routes
@app.route('/payments')
def get_payments():
    authorizationHeader = request.headers.get('authorization')	
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")
    try:
        cur = conn.cursor()

        header = {'Authorization': f'{authorizationHeader}'}

        url = "http://security-service/verify"
        r = requests.post(url, headers = header)

        if r.status_code != 200:
            return jsonify({'success': False, 'details': f'Error while contacting security service. Status code: {r.status_code}'})

        data = json.loads(r.text)

        if not "clientId" in data:
            return jsonify({'success': False, 'details': f'Unauthorized to use this service.'}), 401

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

@app.route('/notifications')
def get_notifications():
    authorizationHeader = request.headers.get('authorization')	
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")
    try:
        cur = conn.cursor()

        header = {'Authorization': f'{authorizationHeader}'}

        url = "http://security-service/verify"
        r = requests.post(url, headers = header)

        if r.status_code != 200:
            return jsonify({'success': False, 'details': f'Error while contacting security service. Status code: {r.status_code}'})

        data = json.loads(r.text)

        if not "clientId" in data:
            return jsonify({'success': False, 'details': f'Unauthorized to use this service.'}), 401

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

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)