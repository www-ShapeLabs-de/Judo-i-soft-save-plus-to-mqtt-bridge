#!/usr/bin/python3
# -*- coding: utf-8 -*-

#Judo Config
JUDO_USER = "myjudousername"
JUDO_PASSWORD = "myjudopassword"

#MQTT Config
BROKER = "192.168.1.2"              #Broker IP
USE_MQTT_AUTH = True                #Set true, if user/pw authentification on broker, set false, if using anonymous login
MQTTUSER = "mqttuser"               #only required if USE_MQTT_AUTH = True
MQTTPASSWD = "mosquitto"            #only required if USE_MQTT_AUTH = True
PORT = 1883                         #MQTT PORT, 1883 default standard

#General Config
LOCATION = "my_location"            #Location of Judo device
NAME = "Judo_isoftsaveplus"         #Name of Judo device
MANUFACTURER = "ShapeLabs.de"       #CC BY-NC-SA 4.0
SW_VERSION = "2.0"
STATE_UPDATE_INTERVAL = 20          #Update interval in seconds
AVAILABILITY_ONLINE = "online"
AVAILABILITY_OFFLINE = "offline"

#Error- and warning messages of plant published to notification topic ( LOCATION/NAME/notify ). Can be used for hassio telegram bot..
LANGUAGE = "DE"                     # "DE" / "ENG"
MQTT_DEBUG_LEVEL = 2                # 0=0ff, 1=Judo-Warnings/Errors, 2=Command feedback  3=Script Errors, Exceptions
MAX_RETRIES = 3

# The maximum slider values that can be set for leakage protection can be limited here. 
# The limitation can be useful to improve the handling of the sliders in the Homeassistant. 
LIMIT_EXTRACTION_TIME = 60          #can setup to max 600min 
LIMIT_MAX_WATERFLOW = 3000          #can setup to max 5000L/h 
LIMIT_EXTRACTION_QUANTITY = 500     #can setup to max 3000L

APPDAEMON = True                    #'True' , if running in Appdaemon docker directly in HA, on generic Linux platform set flag to 'False'
# for Appdaemon the whole path is required "/config/appdaemon/apps/main/temp_getjudo.pkl", otherwise "temp_getjudo.pkl"
TEMP_FILE = "/config/appdaemon/apps/main/temp_getjudo.pkl"
#TEMP_FILE = "temp_getjudo.pkl"
