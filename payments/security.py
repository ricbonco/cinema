import os
import json
from datetime import datetime  
from datetime import timedelta  

import psycopg2

from dotenv import load_dotenv
load_dotenv()

import hashlib

# Get environment variables
DBNAME = os.getenv('DBNAME')
DBUSER = os.getenv('DBUSER')
DBPASSWORD = os.getenv("DBPASSWORD")

def authenticate(clientId, clientSecret):

    conn = None
    hash_object = hashlib.sha1(bytes(clientSecret, 'utf-8'))
    hashed_client_secret = hash_object.hexdigest()
    query = "select * from public.clients where \"ClientId\"='" + clientId + "' and \"ClientSecret\"='" + hashed_client_secret + "'"
    try:
        conn = psycopg2.connect("host='security_postgres' dbname=" + DBNAME + " user=" + DBUSER +" password=" +DBPASSWORD)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        isAdmin = False
        isEmployee = False

        print(rows, flush=True)

        print(cur.rowcount, flush=True)

        if cur.rowcount == 1:
            for row in rows:
                isAdmin = row[3]
                isEmployee = row[4]
                break

            response = authResponse(isAdmin, isEmployee)
            
            return response.__dict__
        else:
            return False
        
    except (Exception, psycopg2.DatabaseError) as error:
        
        print(error, flush=True)
        if conn is not None:
            cur.close()
            conn.close()

        return False
    finally:
        if conn is not None:
            cur.close()
            conn.close()

class authResponse(dict):
    
    def __init__(self, isAdmin, isEmployee):
        self.isAdmin = isAdmin
        self.isEmployee = isEmployee
