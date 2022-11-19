# Notifications Service

# Import framework
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import requests, psycopg2, smtplib, json, os, psutil
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from security import *
from datetime import datetime

# Instantiate the app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
api = Api(app)

security_mode = os.getenv('SECURITYMODE')
telemetry = os.getenv('TELEMETRY') == 'On'

# Create routes
@app.route('/notify', methods=["POST"])
def post_notify():
    get_telemetry('notifications_start')
    email_address = request.form.get("email_address")
    subject = request.form.get("subject")
    body = request.form.get("body")
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")

    try:
        sender = "cinemacatalog@outlook.com"
        
        cur = conn.cursor()

        get_telemetry('notifications_security_start')
        print("Ricardo 1", flush=True)
        if security_mode == 'Decentralized':

            client_id = request.form.get("client_id")
            client_secret = request.form.get("client_secret")

            print(f"Ricardo client id secret {client_id} secret {client_secret}", flush=True)

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
        get_telemetry('notifications_security_end')
        print("Ricardo 2", flush=True)

        username = data["clientId"] if security_mode == 'Centralized' else client_id

        print("Ricardo 3", flush=True)

        #send_email(sender, email_address, subject, body)

        query = f"""INSERT INTO "notification" ("sender", "recipient", "subject", "body", "time", "username") 
                    VALUES
                    ('{sender}', '{email_address}', '{subject}', '{body}', NOW(), '{username}')
                    returning id"""

        print("Ricardo 4", flush=True)

        dbquery = cur.execute(query)
        id_notification = cur.fetchone()[0]

        updated_rows = cur.rowcount

        if updated_rows is 1:
            conn.commit()
            
            return jsonify({'success': True, 'id_notification' : id_notification, 'sender' : sender, 'recipient' : email_address, 'subject' : subject, 'body' : body})
        else:  
            return jsonify({'success': False, 'details': 'Unable to send notification.'})

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

def send_email(sender, recipient, subject, text):
    #Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = recipient
    message['Subject'] = subject
    #The body and the attachments for the mail
    message.attach(MIMEText(text, 'plain'))
    #Create SMTP session for sending the mail
    session = smtplib.SMTP("smtp-mail.outlook.com", port=587)
    session.starttls() #enable security
    session.login(sender, "C1n3m@!2022*") #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender, recipient, text)
    session.quit()

def get_telemetry(operation):
    if telemetry:
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        log(f"{datetime.now()},{operation},{cpu_usage},{ram_usage}")

def log(text):
    file = open("notifications.csv", "a")  
    file.write(f"{text}\n")
    file.close() 

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)