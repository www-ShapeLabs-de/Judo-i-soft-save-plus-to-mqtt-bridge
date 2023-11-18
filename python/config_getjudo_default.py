#!/usr/bin/python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
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

USE_SODIUM_CHECK = True             #'True' activates the monitoring of the sodium limit when the water hardness is set
SODIUM_INPUT = 30                   #Sodium level of input water [mg/L]. Ask your water provider or check providers webpage
SODIUM_LIMIT = 200                  #Sodium limit value. Default 200mg/L (Germany)

#The environment in which the script will run. Select "True" if you want to run it in the Appdeamon, or set "False" if you want to run the script on a generic Linux.
RUN_IN_APPDEAMON = True

#Set this Flag to True, if you've a Judo Softwell P. There are no functions for leakage protection, no battery-,salt- & softwatersensor
USE_WITH_SOFTWELL_P = False
#-------------------------------------------------------------------------------

# for Appdaemon the whole path is required "/config/appdaemon/apps/main/temp_getjudo.pkl", otherwise "temp_getjudo.pkl"
if RUN_IN_APPDEAMON == True:
    TEMP_FILE = "/config/apps/main/temp_getjudo.pkl"
else:
    TEMP_FILE = "temp_getjudo.pkl"
