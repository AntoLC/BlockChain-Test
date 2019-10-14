#!flask/bin/python
from flask import Flask, jsonify, request
from blockchain import Blockchain
from api_routes import APIApp
from uuid import uuid4

if __name__ == '__main__':
    APIApp().run(debug=True, host='0.0.0.0')
