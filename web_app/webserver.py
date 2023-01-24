#!/usr/bin/env python3
# revision 1.0
# 28 May 2021

import os
from flask import Flask, render_template, request, redirect
from flask.helpers import url_for
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import simplejson as json
import syslog

app = Flask(__name__)
broker_address = "10.20.30.8"
auth = {
        'username':"point",
        'password':"mqtt"
}

mqtt_content = {
  "position" : 0, 
  "shot": [ -1, -1, -1, -1, -1 ]
}

@app.route('/')
def index():
    return 'Error, use number from 0 to 2 after slash"'

@app.route("/<Position>")
def main(Position) :
   global mqtt_content
   try:
     myPos = int(Position)
   except :     
       return ("Error, use number from 0 to 2 after slash")
   if myPos >= 0 and myPos < 3 :
       mqtt_content["position"] = Position
       return render_template('main.html', **mqtt_content)
   else :
       return ("Error, use number from 0 to 2 after slash")
 
@app.route("/shot/<changeShot>/<action>")
def action(changeShot, action):
  global mqtt_content

  # If the action part of the URL is "on," execute the code indented below:
  if action == "hit":
        mqtt_content["shot"][int(changeShot)] = 0
  if action == "miss":
        mqtt_content["shot"][int(changeShot)] = 1
  if action == "reset":
        mqtt_content["shot"] = [ -1, -1, -1, -1, -1 ]

  publish.single("AlphaBravo/Shot",
                payload=json.dumps(mqtt_content),
                hostname=broker_address,
                client_id="WebServer",
                auth=auth)

  return redirect(request.referrer)
  #render_template('main.html', **mqtt_content)
  #redirect(request.referrer)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=False, threaded=True)
