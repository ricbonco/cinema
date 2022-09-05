# Movies Service

# Import framework
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import requests, psycopg2, json

# Instantiate the app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
api = Api(app)

# Create routes
@app.route('/bookings')
def get_movies():
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")
    cur = conn.cursor()
    dbquery = cur.execute("SELECT * FROM movies")
    result = cur.fetchall()
    return jsonify(result)

@app.route('/reserve_seats', methods=["POST"])
def post_reserve_seats():
    id_movie_time = request.form.get("id_movie_time")
    id_seat_type = request.form.get("id_seat_type")
    requested_seats = int(request.form.get("requested_seats"))
    
    available_seats = -1
    id_movie_seat = -1
    ticket_type = ""

    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")
    try:
        
        cur = conn.cursor()
        url = "http://cinema_catalog-service/movie_seats_venue_times"
        body = {'id_movie_time': id_movie_time}
        r = requests.post(url, data = body)

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

        if updated_rows is 1:
            conn.commit()
            return jsonify({'reserved_seats': requested_seats, 'ticket_type': ticket_type})
        else:  
            return jsonify({'success': False, 'details': 'Error while reserving requested seats.'})
        
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