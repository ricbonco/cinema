from flask import Flask, request, jsonify
import json
import hashlib

import authModel

# instantiate the Flask app.
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# API Route for checking the client_id and client_secret
@app.route("/auth", methods=["POST"])
def auth():	
    # get the client_id and secret from the client application
    client_id = request.form.get("client_id")
    client_secret_input = request.form.get("client_secret")

    # the client secret in the database is "hashed" with a one-way hash
    hash_object = hashlib.sha1(bytes(client_secret_input, 'utf-8'))
    hashed_client_secret = hash_object.hexdigest()

    # make a call to the model to authenticate
    authentication = authModel.authenticate(client_id, hashed_client_secret)
    if authentication == False:
        return jsonify({'success': False})
    else: 
        return json.dumps(authentication)

# API route for verifying the token passed by API calls
@app.route("/verify", methods=["POST"])
def verify():
    # verify the token 
    authorizationHeader = request.headers.get('authorization')	
    token = authorizationHeader.replace("Bearer ","")
    verification = authModel.verify(token)
    return jsonify(verification)

@app.route("/logout", methods=["POST"])
def logout():
    token = request.form.get("token")
    status = authModel.blacklist(token)
    return jsonify({'success': status})

@app.route("/client", methods=["POST","DELETE"])
def client():
    if request.method == 'POST':
        # verify the token 
        authorizationHeader = request.headers.get('authorization')	
        token = authorizationHeader.replace("Bearer ","")
        print("Ricardo token " + token, flush=True)
        verification = authModel.verify(token)
        print("Ricardo is admin " + str(verification.get("isAdmin")), flush=True)


        if verification.get("isAdmin") == True:
            # get the client_id and secret from the client application
            client_id = request.form.get("client_id")
            print("Ricardo client id " + client_id, flush=True)
            client_secret_input = request.form.get("client_secret")
            print("Ricardo secret " + client_secret_input, flush=True)
            is_admin = request.form.get("is_admin")
            print("Ricardo is_admin " + is_admin, flush=True)

            # the client secret in the database is "hashed" with a one-way hash
            hash_object = hashlib.sha1(bytes(client_secret_input, 'utf-8'))
            hashed_client_secret = hash_object.hexdigest()

            # make a call to the model to authenticate
            createResponse = authModel.create(client_id, hashed_client_secret, is_admin)
            return jsonify({'success': createResponse})
        else:
            return jsonify({'success': False, 'message': 'Access Denied'})
        
    elif request.method == 'DELETE':
        # not yet implemented
        return jsonify({'success': False})
    else:        
        return jsonify({'success': False})

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)