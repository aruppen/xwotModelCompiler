#!flask/bin/python

"""Alternative version of the ToDo RESTful server implemented using the
Flask-RESTful extension."""

from flask import Flask, jsonify, abort, request, make_response, url_for
from flask.views import MethodView
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from flask.ext.httpauth import HTTPBasicAuth
from flask import request

from Arduino_Monitor import SerialData as DataGen
from ZeroconfigService import ZeroconfService
import socket
import json
 
app = Flask(__name__, static_url_path = "")
api = Api(app)
auth = HTTPBasicAuth()
 
@auth.get_password
def get_password(username):
    if username == 'miguel':
        return 'python'
    return None
 
@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'message': 'Unauthorized access' } ), 403)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog

datagen = DataGen(port="/dev/ttyACM0")    

$resourcedef

$pathdef

if __name__ == '__main__':
	text_entry = ["User=ruppena", "Location=Fribourg", "Name=Udoo Temperature", "Address=Bvd de Perolles 90, 1700 Fribourg"]
	service = ZeroconfService(name="Temperature (a) - "+socket.gethostname(),  port=9000,  text=text_entry)
	service.publish()
	app.run(debug = True)
