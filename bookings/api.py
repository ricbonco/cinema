# Bookings Service

# Import framework
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import requests, psycopg2, json

# Instantiate the app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
api = Api(app)

# Create routes
@app.route('/book', methods=["POST"])
def post_book_seats():
    authorizationHeader = request.headers.get('authorization')	
    id_movie_time = request.form.get("id_movie_time")
    id_seat_type = request.form.get("id_seat_type")
    requested_seats = int(request.form.get("requested_seats"))
    
    available_seats = -1
    id_movie_seat = -1
    ticket_type = ""

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

        username = data["clientId"]

        url = "http://cinema_catalog-service/movie_seats_venue_times"
        body = {'id_movie_time': id_movie_time}
        r = requests.post(url, data = body, headers = header)

        if r.status_code != 200:
            return jsonify({'success': False, 'details': f'Error while contacting cinema catalog service. Status code: {r.status_code}'})

        data = json.loads(r.text)
        seats = data["movie_seats_venue_times"]
        for seat_group in seats:
            if seat_group["id_seat_type"] is int(id_seat_type):
                available_seats = seat_group["available_seats"]
                id_movie_seat = seat_group["id_movie_seat"]
                ticket_type = seat_group["ticket_type"]


        if available_seats is -1:
            return jsonify({'success': False, 'details': 'Error while reserving requested seats.'})
        if available_seats < requested_seats:
            return jsonify({'success': False, 'details': 'Requested seat number is not available.'})

        query = f"""UPDATE movie_seat SET available_seats = {available_seats - requested_seats} 
                   WHERE id = {id_movie_seat}"""

        print("query " + str(query), flush=True)

        dbquery = cur.execute(query)

        updated_rows = cur.rowcount

        if updated_rows is 0:
            conn.rollback()
            return jsonify({'success': False, 'details': 'Error while booking requested seats.'})

        query = f"""INSERT INTO "booking" ("id_movie_seat", "reserved_seats", "time", "username") 
                    VALUES
                    ('{id_movie_seat}', {requested_seats}, NOW(), '{username}')
                    returning id"""

        print("query " + str(query), flush=True)

        dbquery = cur.execute(query)
        id_booking = cur.fetchone()[0]

        updated_rows = cur.rowcount

        if updated_rows is 1:
            conn.commit()
            
            return jsonify({'id_booking': id_booking, 'booked_seats': requested_seats, 'ticket_type': ticket_type})
        else:  
            return jsonify({'success': False, 'details': 'Error while booking requested seats.'})
        
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