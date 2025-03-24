from flask import Flask, jsonify
from aws_wsgi import response

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify(message="Hello from Flask running on Lambda!")

def handler(event, context):
    return aws_wsgi.response(app, event, context) 
