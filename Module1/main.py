#!flask/bin/python
from flask import Flask, jsonify, request
from Module1.blockchain import Blockchain
from Module1.flaskrun import flaskrun
from api_routes import APIApp
from uuid import uuid4

if __name__ == '__main__':
    flaskrun(APIApp())
