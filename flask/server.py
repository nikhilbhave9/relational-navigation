# Import external modules
from flask import Flask
from flask import request
from pymongo import MongoClient

# Import internal modules
from main import main

app = Flask(__name__)

@app.route('/instructions')
def parse_request():
    source = request.args.get('key1')
    destination = request.args.get('key2')

    # ----------------------------------------------------

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb+srv://admin:adminpassword@serverlessinstance0.xphpq.mongodb.net/?retryWrites=true&w=majority"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)
    db = client['main_db']

    # ----------------------------------------------------
    
    # Call the main function and let it handle all the logic
    
    # instructions = main(source, destination, client, db, additional_params=None)

    # return the instructions


    return main(client, 'main_db', 'AC02 010', 'AC02 110', None)

if __name__ == '__main__':
    app.run(debug=True)