# Movies Service

# Import framework
from operator import mod
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import requests, psycopg2, json, random

# Instantiate the app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
api = Api(app)

# Create routes
@app.route('/subtotal')
def get_subtotal():
    id_booking = request.form.get("id_booking")
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")
    try:
        cur = conn.cursor()
        
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

@app.route('/pay', methods=["POST"])
def make_payment():
    id_booking = request.form.get("id_booking")
    card_number = request.form.get("card_number")
    expiration_date = request.form.get("expiration_date")
    card_verification_value = request.form.get("card_verification_value")
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")
    
    try:
        # TODO: Validate if payment already done before doing it
        cur = conn.cursor()

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

        query = f"""INSERT INTO "payment" ("id_booking", "approved", "last_digits", "time") 
                    VALUES
                    ('{id_booking}', {payment_approved}, {card_number[-3:]}, NOW())
                    returning id"""

        dbquery = cur.execute(query)
        id_payment = cur.fetchone()[0]

        updated_rows = cur.rowcount

        if updated_rows is 1:
            conn.commit()
            
            if payment_approved:
                return jsonify({'payment': {'approved' : True, 'id_payment' : id_payment, 'amount' : payment_amount}})
            else:
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

def make_payment(card_number, expiration_date, card_verification_value, amount):
    # Simulate VPOS payments with pseudo random nummbers
    return mod(random.randint(0, 8), 8) is not 0

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)