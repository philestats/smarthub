#!/bin/python

# -------------------------------------------------------------
# display temperature + humidity + pressure data in fullscreen mode
# data are read from a mqtt topic
# deps: paho-mqtt simplejson
# pip install paho-mqtt
# pip install simplejson
# http://www.eclipse.org/paho/clients/python/docs/#client
# -------------------------------------------------------------

import os
from time import sleep, gmtime, strftime
import paho.mqtt.client as mqtt
import simplejson as json
import socket
import requests
import csv
import sys
import ConfigParser

state="STATE_WAIT_DATA"

deviceId='N/A'
dateMsg='N/A'
values='N/A'
data='N/A'
unit='N/A'

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("data/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global state
    print("Message")
    decode_json_data_msg(msg.payload)
    state="STATE_DATA_AVAIL"

def decode_json_data_msg(strMsg):
    global state
    print("decode msg") 
    print(strMsg) 
    try:
        decoded = json.loads(strMsg)
        global deviceId 
        global thingspeakApiKey_teleinfo
        global HCindex_previous
        global HPindex_previous
        global tarif_previous
        deviceId=decoded['id']
        intensity=decoded['I']
        power=decoded['P']
        HCindex=decoded['HC']
        HPindex=decoded['HP']
        print ("----> device Id = ", deviceId)
        print ("----> I = ", intensity)
        print ("----> P = ", power)
        print ("----> HC = ", HCindex)
        print ("----> HP = ", HPindex)
        if (HCindex==HCindex_previous):
            tarif="HP"
        elif (HPindex==HPindex_previous):
            tarif="HC"
        else:
            tarif="unknown"
        print ("tarif={}".format(tarif))
        if (tarif_previous != "unknown"):
            if (tarif != tarif_previous):
                print("Basculse tarif {} -> {}".format( tarif_previous, tarif))
        HCindex_previous=HCindex
        HPindex_previous=HPindex
        tarif_previous=tarif
        req=("https://api.thingspeak.com/update?api_key={}&field1={}&field2={}").format(thingspeakApiKey_teleinfo, power, intensity)
        requests.get(req)

    except (ValueError, KeyError, TypeError):
        print "JSON format error 0"
	# jdateMesg=decoded['date']
	#values=decoded['values']
	#strValues=str(values)
	#strValues=strValues.replace("u\'", "\"")
	#strValues=strValues.replace("\'", "\"")

	

    state="STATE_WAIT_DATA"
# -----------------------------------------------------------

client = mqtt.Client(protocol=mqtt.MQTTv31)
client.on_connect = on_connect
client.on_message = on_message

print "start"
# MQTT connection
client.username_pw_set("admin", "admin")
client.connect("localhost", 1883)
client.loop_start()
print ("MQTT connection OK")


config = ConfigParser.RawConfigParser()
config.read('conf/hub.conf')
thingspeakApiKey_teleinfo = config.get('thingspeak', 'teleinfo')


HCindex_previous=0
HPindex_previous=0
tarif_previous="unknown"

def display_data():
    global state
    print("display: data")
    print "deviceId ", deviceId


    state="STATE_WAIT_DATA"

def display_wait_data():
    print("display: wait for data")      

while True:
    if (state=="STATE_DATA_AVAIL"):
        display_data()

 






