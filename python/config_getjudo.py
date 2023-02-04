#!/urs/bin/python3
# -*- coding: utf-8 -*-

#Judo Config
JUDO_USER = "myjudousername"
JUDO_PASSWORD = "myjudopassword"

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

#Error- and warning messages of plant published to notification topic ( LOCATION/NAME/notify ). Can be used for hassio telegram bot..
LANGUAGE = "DE"									# "DE" / "ENG"
MQTT_DEBUG_LEVEL = 3							# 0=0ff, 1=Judo-Warnings/Errors, 2=Command feedback  3=Script Errors, Exceptions
MAX_RETRIES = 3

# for Appdaemon the whole path is required "/config/appdaemon/apps/Judo/temp_getjudo.pkl", otherwise "temp_getjudo.pkl"
TEMP_FILE = "/config/appdaemon/apps/main/temp_getjudo.pkl"
APPDAEMON = True                                # if running in Appdaemon docker


