#!flask/bin/python
from api_routes import APIApp

if __name__ == '__main__':
    APIApp().run(debug=True, host='0.0.0.0')
