#!/usr/bin/env python3
# Display the text from MQQT topics with double-buffering.
# 28-May-2020
# revision 1.0

from samplebase import SampleBase
from rgbmatrix import graphics
import threading
import time
import math

# MQTT section
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import simplejson as json #import json

# MQTT data
# brocker IP, topic, we are
mqtt_ip = "172.21.10.15"
mqtt_topic =  [ "AlphaBravo/Direction", "AlphaBravo/Speed", "AlphaBravo/Shot" ]
mqtt_client = "P1"
isConnected = False
# data to connect
user = "point"
password = "mqtt"
#structure for publish
auth = {
        'username':"client",
        'password':"mqtt"
}

to_display = {
   # direction in degreese
   # speed in m/s
   # shot can be -1 == no result, 0 - miss, 1 hit
   0: { "direction" : 0.0, "speed" :  0.0,  "shot" : [ -1, -1, -1, -1, -1 ], "color" : graphics.Color(255, 0, 255) },
   1: { "direction" : 0.0, "speed" :  0.0,  "shot" : [ -1, -1, -1, -1, -1 ], "color" : graphics.Color(0, 255, 0) },
   2: { "direction" : 0.0, "speed" :  0.0,  "shot" : [ -1, -1, -1, -1, -1 ], "color" : graphics.Color(0, 0, 255) },
   3: { "direction" : 0.0, "speed" :  0.0,  "shot" : [ -1, -1, -1, -1, -1 ], "color" : graphics.Color(0, 0, 0) },
   4: { "direction" : 0.0, "speed" :  0.0,  "shot" : [ -1, -1, -1, -1, -1 ], "color" : graphics.Color(0, 0, 0) }
   }

# to specify what 3 from 5 will be displayed
to_Disp_list = [ 0, 1, 2 ]

class DispText(SampleBase):
    def __init__(self):
        super(DispText, self).__init__(self)

    def run(self):
        global isConnected
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("fonts/5x7.bdf")
        offscreen_canvas.Clear()
        frame = 22
        while True :
          shotPos = 0;
          for myDisp in to_Disp_list:
            # display arrow
            line_start_x = frame/2 + frame * shotPos
            line_start_y = 8
            line_length = 6
            # translate angle to radians
            angle = (to_display[myDisp]['direction'] - 90)* 3.14 / 180.0
            line_end_x= line_start_x + round(math.cos(angle),2)*line_length
            line_end_y = line_start_y + round(math.sin(angle),2)*line_length
            # clear space
            self.draw_box(offscreen_canvas, line_start_x-line_length-1, line_start_y+line_length, line_length * 2 + 2, line_length * 2 + 2, graphics.Color(0, 0, 0))
            graphics.DrawCircle(offscreen_canvas, line_start_x, line_start_y, 1, to_display[myDisp]['color'])
            # outline circle
            graphics.DrawCircle(offscreen_canvas, line_start_x, line_start_y, 1+line_length, to_display[myDisp]['color'])
            if isConnected :
              graphics.DrawLine(offscreen_canvas, line_start_x, line_start_y, line_end_x, line_end_y, graphics.Color(255, 255, 0))
            else :
              graphics.DrawLine(offscreen_canvas, line_start_x, line_start_y, line_end_x, line_end_y, graphics.Color(0,0,0))
            #display speed
            x = -22
            y = 24
            speed = round(float(to_display[myDisp]['speed']),1)
            # we have to hide the first number + jump to the next symbol
            self.draw_box(offscreen_canvas, x + frame * (shotPos + 1), y, frame, 7, graphics.Color(0,0,0))
            if speed < 10.0 :
               x = x + 5
            if isConnected :
              graphics.DrawText(offscreen_canvas, font, x + frame * (shotPos + 1), y, to_display[myDisp]['color'], str(speed))
            else :
              graphics.DrawText(offscreen_canvas, font, x + frame * (shotPos + 1), y, graphics.Color(0,0,0), str(speed))
            #display shots
            bBot = 30
            bSize = 3
            bHeight = 5
            shots = to_display[shotPos]['shot']
            ii = range(0, len(shots))
            for sNum in ii :
              posX = frame * shotPos + sNum * (bSize + 1)
              # clear the space
              self.draw_box(offscreen_canvas, posX, bBot, bSize-1, bHeight, graphics.Color(0, 0, 0))
              if shots[sNum] == -1:
                 graphics.DrawLine(offscreen_canvas, posX, bBot, posX+bSize-1, bBot,    to_display[myDisp]['color'])
              if shots[sNum] == 0:
                 self.draw_box(offscreen_canvas, posX, bBot, bSize-1, bHeight, graphics.Color(255, 0, 0))
              if shots[sNum] == 1:
                 self.draw_box(offscreen_canvas, posX, bBot, bSize-1, bHeight, to_display[myDisp]['color'])
              if not isConnected :
                  self.draw_box(offscreen_canvas, posX, bBot, bSize-1, bHeight, graphics.Color(0, 0, 0))
            shotPos = shotPos + 1
          offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
          time.sleep(0.04)
          # end of while

    def draw_box(self, canvas, xx, yy, width, height, color) :
        for YY in range(0, height):
           graphics.DrawLine(canvas, xx, int(yy-YY), int(xx+width), int(yy-YY) ,color)

def on_disconnect(client, userdata, rc):
            global isConnected
            isConnected = False

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
        global isConnected
        if rc == 0:
            isConnected = True
            for topic in mqtt_topic :
              client.subscribe(topic)
        else:
            print("Connection failed " + str(rc))

def on_message(client, userdata, msg):
     parsed_json = {}
     try :
       parsed_json = json.loads(msg.payload)
       # here we have  to check from what topic we get the message
       if (msg.topic == "AlphaBravo/Direction" ) :
          if (('position' not in parsed_json)  or ('direction' not in parsed_json)) :
            return
          pos = int(parsed_json['position'])
          if pos < 0 and pos > 4 :
            return
          dir = float(parsed_json['direction'])
          if dir >= 0.0 and  dir < 360 :
            to_display[pos]['direction'] = dir

       if (msg.topic == "AlphaBravo/Speed" ) :
          if ('position' not in parsed_json ) or ('speed' not in parsed_json) :
            return
          pos = int(parsed_json['position'])
          if pos < 0 and pos > 4 :
            return
          speed = float(parsed_json['speed'])
          if pos >= 0 and  pos < 50 :
            to_display[pos]['speed'] = speed

       if (msg.topic == "AlphaBravo/Shot" ) :
          if ('position' not in parsed_json)  or ('shot' not in parsed_json) :
            return
          pos = int(parsed_json['position'])
          if pos < 0 and pos > 4 :
            return
          shot = parsed_json['shot']
          if isinstance(shot, list) and len(shot) == 5 :
            to_display[pos]['shot'] = shot

     except:
       print("Error converting:  " + str(msg.payload) + " from topic: " + str(msg.topic))

class procThread (threading.Thread):
   def __init__(self):
      threading.Thread.__init__(self)
      self.thread = None
      self._should_continue = False

   def run(self):
      if not self._should_continue :
        self._should_continue = True
        disp = DispText()
        if (not disp.process()):
          disp.print_help()

   def cancel(self):
        if self.thread is not None:
            self._should_continue = False
            self.thread.cancel()

# Main function
if __name__ == "__main__":

    #define display proc thread
    rH =  procThread()
    rH.start()

    # MQTT related configurations and functions
    client = mqtt.Client(mqtt_client)
    client.username_pw_set(username=user, password=password)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.connect(mqtt_ip, 1883, 60)

    time.sleep(4) # Wait for connection setup to complete

    # reconnect automatically
    client.loop_forever()
