#/bin/zsh

for D in {0..359} ; do 
  (
  mosquitto_pub -h 10.20.30.8 -u "point" -P "mqtt" -t "AlphaBravo/Direction" -m '{ "position":"0", "direction":"'$D'" } ' 
  ) done
sleep 3 
for D in {0..40} ; do
 (
 mosquitto_pub -h 10.20.30.8 -u "point" -P "mqtt" -t "AlphaBravo/Speed" -m '{ "position":"2", "speed":"'$D'" } ' 
 ) done
sleep 3 
mosquitto_pub -h 10.20.30.8 -u "point" -P "mqtt" -t "AlphaBravo/Shot" -m '{ "position":"1", "shot": [ 1, -1, -1, -1, -1 ] } ' 
sleep 0.5
mosquitto_pub -h 10.20.30.8 -u "point" -P "mqtt" -t "AlphaBravo/Shot" -m '{ "position":"1", "shot": [ 1, 1, -1, -1, -1 ] } ' 
sleep 0.5
mosquitto_pub -h 10.20.30.8 -u "point" -P "mqtt" -t "AlphaBravo/Shot" -m '{ "position":"1", "shot": [ 1, 1, -1, -1, -1 ] } ' 
sleep 0.5
mosquitto_pub -h 10.20.30.8 -u "point" -P "mqtt" -t "AlphaBravo/Shot" -m '{ "position":"1", "shot": [ 1, 1, 0, -1, -1 ] } ' 
sleep 0.5
mosquitto_pub -h 10.20.30.8 -u "point" -P "mqtt" -t "AlphaBravo/Shot" -m '{ "position":"1", "shot": [ 1, 1, 0, 0, -1 ] } ' 
sleep 2 
mosquitto_pub -h 10.20.30.8 -u "point" -P "mqtt" -t "AlphaBravo/Shot" -m '{ "position":"1", "shot": [ -1, -1, -1, -1, -1 ] } '
