# Payments Service

# Import framework
from operator import mod
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from datetime import date
import requests, psycopg2, json, random, os, psutil
from security import *
from datetime import datetime

# Instantiate the app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
api = Api(app)

security_mode = os.getenv('SECURITYMODE')
telemetry = os.getenv('TELEMETRY') == 'On'

# Create routes
@app.route('/subtotal')
def get_subtotal():
    get_telemetry('subtotal_start')
    id_booking = request.form.get("id_booking")
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")
    try:
        cur = conn.cursor()

        get_telemetry('subtotal_security_start')
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

            isAdmin = data['isAdmin']
            isEmployee = data['isEmployee']
        get_telemetry('subtotal_security_end')

        query = f"""SELECT b.id AS id_booking, b.reserved_seats * ms.price::numeric::float AS subtotal
                    FROM booking AS b
                    INNER JOIN movie_seat AS ms
                      ON ms.id = b.id_movie_seat 
                        AND b.id = {id_booking}"""
        
        dbquery = cur.execute(query)
        row_headers=[x[0] for x in cur.description] 
        result = cur.fetchall()
        json_data=[]
        for r in result:
            json_data.append(dict(zip(row_headers,r)))
        print(jsonify(json_data), flush=True)  
        return jsonify({'booking': json_data})
        
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
        get_telemetry('subtotal_end')

@app.route('/pay', methods=["POST"])
def make_payment():
    get_telemetry('pay_start')
    id_booking = request.form.get("id_booking")
    card_number = request.form.get("card_number")
    expiration_date = request.form.get("expiration_date")
    card_verification_value = request.form.get("card_verification_value")
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")
    
    try:
        cur = conn.cursor()

        get_telemetry('pay_security_start')
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

            isAdmin = data['isAdmin']
            isEmployee = data['isEmployee']
        get_telemetry('pay_security_end')

        username = data["clientId"] if security_mode == 'Centralized' else client_id

        query = f"""SELECT p.id AS id_payment
                    FROM payment AS p
                    WHERE p.id_booking = {id_booking} 
                       AND p.approved = true"""
        
        dbquery = cur.execute(query)
        row_headers=[x[0] for x in cur.description] 
        result = cur.fetchall()
        
        if len(result) == 1:
            return jsonify({'success': False, 'details': f'Payment already processed.'})

        query = f"""SELECT b.id AS id_booking, b.reserved_seats * ms.price::numeric::float AS payment_amount
                    FROM booking AS b
                    INNER JOIN movie_seat AS ms
                      ON ms.id = b.id_movie_seat 
                        AND b.id = {id_booking}"""
        
        dbquery = cur.execute(query)
        row_headers=[x[0] for x in cur.description] 
        result = cur.fetchall()
        data=[]
        for r in result:
            data.append(dict(zip(row_headers,r)))

        payment_amount = data[0]['payment_amount']

        payment_approved = make_payment(card_number, expiration_date, card_verification_value, payment_amount)

        query = f"""INSERT INTO "payment" ("id_booking", "approved", "last_digits", "time", "username") 
                    VALUES
                    ('{id_booking}', {payment_approved}, {card_number[-4:]}, NOW(), '{username}')
                    returning id"""

        dbquery = cur.execute(query)
        id_payment = cur.fetchone()[0]

        updated_rows = cur.rowcount

        if updated_rows is 1:
            conn.commit()
            
            get_telemetry('pay_notify_start')
            url = "http://notifications-service/notify"

            if payment_approved:
                body = {'email_address': 'cinemacatalogproject@gmail.com', 
                        'subject' : f'Your order {id_payment} has been processed!',
                        'body' : 
                        f"""Your order {id_payment} has been processed succesfully at {date.today()}!
                        Amount: {payment_amount}"""} 

                if security_mode == "Decentralized":
                    body["client_id"] = client_id
                    body["client_secret"] = client_secret

                r = requests.post(url, data = body, headers = header) if security_mode == 'Centralized' else requests.post(url, data = body)
                get_telemetry('pay_notify_end')                

                if r.status_code != 200:
                    return jsonify({'success': False, 'details': f'Error while contacting notification service. Status code: {r.status_code}'})

                return jsonify({'payment': {'approved' : True, 'id_payment' : id_payment, 'amount' : payment_amount}})
            else:
                body = {'email_address': 'cinemacatalogproject@gmail.com', 
                        'subject' : f'Error when processing your order!',
                        'body' : 
                        f"""Your payment of {payment_amount} was declined by your card issuer. Please try again."""}

                if security_mode == "Decentralized":
                    body["client_id"] = client_id
                    body["client_secret"] = client_secret

                r = requests.post(url, data = body, headers = header) if security_mode == 'Centralized' else requests.post(url, data = body)
                get_telemetry('pay_notify_end')

                if r.status_code != 200:
                    return jsonify({'success': False, 'details': f'Error while contacting notification service. Status code: {r.status_code}'})

                return jsonify({'payment': {'approved' : False, 'amount' : payment_amount}})
        else:  
            return jsonify({'success': False, 'details': 'Unable to register payment.'})

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
        get_telemetry('pay_end')

def make_payment(card_number, expiration_date, card_verification_value, amount):
    # Simulate VPOS payments with pseudo random nummbers
    return mod(random.randint(0, 8), 8) is not 0
    # return mod(random.randint(0, 2), 2) is not 0

def get_telemetry(operation):
    if telemetry:
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        log(f"{datetime.now()},{operation},{cpu_usage},{ram_usage}")

def log(text):
    file = open("payments.csv", "a")  
    file.write(f"{text}\n")
    file.close()  

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)