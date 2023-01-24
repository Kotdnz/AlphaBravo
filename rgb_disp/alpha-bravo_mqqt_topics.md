# General conception
Each device must be able to connect to our network, connect to the main MQTT Server (mosquitto) to the predefined topics.

## MQTT server - mosquitto
Mosquitto install and configuration (for mac example):<br>
<code>brew install mosquitto<br>
mosquitto_passwd -c passwordfile point mqtt<br>
specify listener & passwd in /usr/local/etc/mosquitto/mosquitto.conf<br>
/usr/local/sbin/mosquitto -v -c /usr/local/etc/mosquitto/mosquitto.conf</code>

config file real example <p>
<code>cat /usr/local/etc/mosquitto/mosquitto.conf | grep -v "^#" | grep -v "^$"<br>
listener 1883 10.20.30.8<br>
password_file /Users/kot.dnz/tmp/passwordfile</code>
<p>

## Clients - direction
We have 3 anemometrs spreaded along the distance. <br>
Devices numeration - 0, 1 ,2
Each of them should subscribe to the singleo one topic on MQTTServer:
<code>
AlphaBravo/Direction
</code>
and send:
- device position number
- wrapped in JSON the angle in float with <b>two</b> digits after point and devided by point, not comma.<br>
Range: <b>0.00 - 359.99</b>
Other values will be ignored.<br>
<code>
{<br>
"position":"0",<br>
"direction":"300.00"<br>
}<br>
</code>

<p>Testing example for zsh <br>
<code>
for D ({0..359}) mosquitto_pub -h 10.20.30.8 -u "point" -P "mqtt" -t "AlphaBravo/Direction" -m '{ "position":"0", "direction":"'$D'" } '
</code>

## Clients - anemometr
The same approach is for anemometr<br>
Topic:

<code>
AlphaBravo/Speed
</code>

Speed value in m/s in float with <>bone<.b> digits after point and devided by point, not comma.<br>
Range: <b>0.0 - 49.9</b>
Other values will be ignored.<br>

<code>
{<br>
"position":"1",<br>
"speed":"3.2"<br>
}<br>
</code>

## Clients - Web upplication for judjes to indicate hit/miss
Every shooting position contains place to display result after the 5 shoots.
- value -1 mean - we are ready to serve - symbol underline
- value 0 mean - miss - position's color solid box
- value 1 mean - hit - red color solid box

The screen layout:
5 rows with two columns: left call contains button hit, right miss 
The 6 rows has only one button - reset. 

Before the next shift, judje reset the display<<br>
Every shot judje marking as hit or miss.

<code>
AlphaBravo/Shot
</code>

JSON example to reset 
<code>

{<br>
"position":"2",<br>
"shot": [ -1, -1, -1, -1, -1 ]<br>
}<br>
</code>


## Consumer - RGB display
> Important: this python3 app has a bug - not starting if MQTT is unreachable or impossible to connect.

Application has two different thread
- first take care about diplaying 
- second one - subscribed to topics and change the diplay array according to the latest values

If we lost the connection - they will be restored automaticall. During connection no any values will be diplayed.

