#!flask/bin/python
from Module1.flaskrun import flaskrun
from Module1.api_routes import APIApp

if __name__ == '__main__':
    flaskrun(APIApp())
