#!/urs/bin/python3
# -*- coding: utf-8 -*-

#Judo Config
TOKEN = "1a2b3c4d5e6f1a2b3c4d5e6f1a2b3c4d"      #Just take the knmtoken from URL

#MQTT Config
BROKER = "192.168.1.2"                          #Broker IP
USE_MQTT_AUTH = True                            #Set true, if user/pw authentification on broker, set false, if using anonymous login
MQTTUSER = "my_mqttuser"                        #only required if USE_MQTT_AUTH = True
MQTTPASSWD = "my_mqttpasswd"                    #only required if USE_MQTT_AUTH = True
PORT = 1883                                     #MQTT PORT, 1883 default standard


#General Config
LOCATION = "my_location"                        #Location of Judo device
NAME = "Judo_isoftsaveplus"                     #Name of Judo device
MANUFACTURER = "ShapeLabs.de"                   #CC BY-NC-SA 4.0
SW_VERSION = "1.3"
STATE_UPDATE_INTERVAL = 20                      #Update interval in seconds
AVAILABILITY_ONLINE = "online"
AVAILABILITY_OFFLINE = "offline"



