# Movies Service

# Import framework
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import requests, psycopg2, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Instantiate the app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
api = Api(app)

# Create routes
@app.route('/notify', methods=["POST"])
def get_movies():
    email_address = request.form.get("email_address")
    subject = request.form.get("subject")
    body = request.form.get("body")
    conn = psycopg2.connect("host='postgres' dbname='cinema' user='postgres' password='cinema123'")

    try:
        sender = "cinemacatalog@outlook.com"
        
        cur = conn.cursor()

        send_email(sender, email_address, subject, body)

        query = f"""INSERT INTO "notification" ("sender", "recipient", "subject", "body", "time") 
                    VALUES
                    ('{sender}', '{email_address}', '{subject}', '{body}', NOW())
                    returning id"""

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

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)