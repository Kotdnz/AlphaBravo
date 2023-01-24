#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

#define DEBUG 0

// data to adjust
char* ssid = "LRSC";
char* password =  "Lrsc2019!";
const char* mqttServer = "172.21.10.15";

// code section
char* sensorPosition = "4";  // Devices numeration - 0, 1 ,2 based on Jumper position. No jumper - 0, to JMP0-JMP1 = 1, JMP0-JMP2 = 2.

const int   mqttPort = 1883;
const char* mqttUser = "point";
const char* mqttPassword = "mqtt";
const char* mqttTopicDir = "AlphaBravo/Direction";
const char* mqttTopicSpd = "AlphaBravo/Speed";
const char* mqttWelcome  = "AlphaBravo/Welcome";

#define ANEMOMETER_PIN 14
#define VANE_PIN A0
volatile unsigned long last_micros_an;

float dirDeg[] = {112.5,67.5,90,157.5,135,202.5,180,22.5,45,247.5,225,337.5,0,292.5,315,270};
int sensorMin[] = {60, 93,101,130,198,257,300,418,471,604,649,707,784,845,896,954};
int sensorMax[] = {84,100,116,154,218,285,332,462,521,648,695,781,845,895,953,1033};

#define CALC_INTERVAL 1000
#define DEBOUNCE_TIME 15

unsigned long nextCalc;
unsigned long timer;
unsigned long cSpd;

int windDir;
int windSpeed;
int rainAmmount;

WiFiClient WiFiclient;
PubSubClient client(WiFiclient);

int ledState = LOW;
#define LED_B 2

void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    if (DEBUG) Serial.print(".");
  }

  randomSeed(micros());
  
  if (DEBUG) Serial.println("WiFi connected.");
  if (DEBUG) Serial.println(WiFi.localIP());
}

ICACHE_RAM_ATTR void SpeedCount() {
  if((long)(micros() - last_micros_an) >= DEBOUNCE_TIME * 1000) {
     cSpd = cSpd + 1;
     last_micros_an = micros();
  }
}

void setup() {
  if (DEBUG) Serial.begin(115200); 

  pinMode(ANEMOMETER_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ANEMOMETER_PIN), SpeedCount, RISING);
  
  setup_wifi();
  client.setServer(mqttServer, mqttPort);

  // blinking
  pinMode(LED_B, OUTPUT);
}

void loop() {
  timer = millis();
  
  int incoming = 0;
  long windSpeed;
  float windDirection;

  if(timer > nextCalc)
  {
    StaticJsonDocument<100> wDir;
    StaticJsonDocument<100> wSpeed;
    char msg[100];
    nextCalc = timer + CALC_INTERVAL;
    // Direction
    incoming = analogRead(windDir);
    if (DEBUG) Serial.print("A0 read: ");
    if (DEBUG) Serial.print(incoming);
    for(int i=0; i<=15; i++) {
     if(incoming >= sensorMin[i] && incoming <= sensorMax[i]) {
      windDirection = dirDeg[i];
      break;
     } 
    }

    /* 
    AlphaBravo/Direction
    {
      "position":"0",
      "direction":"300.00"
    } */
    wDir["position"] = sensorPosition;
    wDir["direction"] = windDirection;
    serializeJson(wDir, msg);
    client.publish(mqttTopicDir, msg);
    if (DEBUG) Serial.print(", Wind Direction: ");
    if (DEBUG) serializeJson(wDir, Serial);
    if (DEBUG) Serial.println("");
    // Wind Speed
    /*
     * AlphaBravo/Speed
     * {
        "position":"1",
        "speed":"3.2"
        }
     */
    wSpeed["position"] = sensorPosition;
    wSpeed["speed"] = (float)(cSpd * 0.666);
    // mutex to avoid to change the variable from two places simultanious
    noInterrupts(); 
      cSpd = 0;
    interrupts();
    serializeJson(wSpeed, msg);
    client.publish(mqttTopicSpd, msg);
    
    if (DEBUG) Serial.print(", Wind speed: ");
    if (DEBUG) serializeJson(wSpeed, Serial);
    if (DEBUG) Serial.print(" ");

    /* Serial.print("Gusting at: ");
    Serial.print(windGust / 10);
    Serial.print('.');
    Serial.print(windGust % 10);
    Serial.println("");
    */

    if (!client.connected()) {
      reconnect();
    } 
    client.loop();
    if (ledState == LOW) {
      ledState = HIGH;  // Note that this switches the LED *off*
    } else {
      ledState = LOW;  // Note that this switches the LED *on*
    }
    digitalWrite(LED_B, ledState);
    
    // need this delay to work with MQTT without reconnects
    delay(1000);
  }
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    if (DEBUG) Serial.println("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-Position-";
    clientId += sensorPosition;
    // Attempt to connect
    if (client.connect(clientId.c_str(), mqttUser, mqttPassword)) {
      if (DEBUG) Serial.println("MQTT connected.");
      // Once connected, publish an announcement...
      clientId += " connected to MQTT server";
      client.publish(mqttWelcome, clientId.c_str(), true);
      // ... and resubscribe if needs
      //client.subscribe(mqttTopicDir);
      //client.subscribe(mqttTopicSpd);
    } else {
      if (DEBUG) Serial.print("failed, rc=");
      if (DEBUG) Serial.print(client.state());
      if (DEBUG) Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}
