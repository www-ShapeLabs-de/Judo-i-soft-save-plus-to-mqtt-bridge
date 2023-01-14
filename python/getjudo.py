#!/urs/bin/python3
# -*- coding: utf-8 -*-

import urllib3
import json
import time
import gc
import config_getjudo
import hashlib
import sys
from paho.mqtt import client as mqtt

class entity():
    def __init__(self, name, icon, entity_type, unit = "", minimum = 1, maximum = 100, step = 1, value = 0):
        self.name = name
        self.unit = unit
        self.icon = icon
        self.entity_type = entity_type #total_inc, sensor, number, switch, 
        self.value = value
        self.minimum = minimum
        self.maximum = maximum
        self.step = step

    def send_entity_autoconfig(self):
        device_config = {
            "identifiers": f"[{client_id}]",
            "manufacturer": config_getjudo.MANUFACTURER,
            "model": config_getjudo.NAME,
            "name": client_id,
            "sw_version": config_getjudo.SW_VERSION
        }

        entity_config = {
            "device": device_config,
            "availability_topic": availability_topic,
            "state_topic": state_topic,
            "name": client_id + " " + self.name,
            "unique_id": client_id + "_" + self.name,
            "icon": self.icon,
            "value_template": "{{value_json." + self.name + "}}"
        }

        if self.entity_type == "total_increasing":
            entity_config["device_class"] = "water"
            entity_config["state_class"] = self.entity_type
            entity_config["unit_of_measurement"] = self.unit
            self.entity_type = "sensor"

        elif self.entity_type == "number":
            entity_config["command_topic"] = command_topic
            entity_config["unit_of_measurement"] = self.unit
            entity_config["min"] = self.minimum
            entity_config["max"] = self.maximum
            entity_config["step"] = self.step
            entity_config["command_template"] = "{\"" + self.name + "\": {{ value }}}"

        elif self.entity_type == "switch":
            entity_config["command_topic"] = command_topic
            entity_config["payload_on"] = "{\"" + self.name + "\": 1}"
            entity_config["payload_off"] = "{\"" + self.name + "\": 0}"
            entity_config["state_on"] = 1
            entity_config["state_off"] = 0

        elif self.entity_type == "sensor":
            entity_config["unit_of_measurement"] = self.unit

        else:
            print ("autoconf ERROR!!")

        autoconf_topic = f"homeassistant/{self.entity_type}/{config_getjudo.LOCATION}/{config_getjudo.NAME}_{self.name}/config"
        publish_json(client, autoconf_topic, entity_config)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker...")
        client.subscribe(command_topic)
        print("Topics has been subscribed...")
        
        client.publish(availability_topic, config_getjudo.AVAILABILITY_ONLINE, qos=0, retain=True)

        for obj in gc.get_objects():
            if isinstance(obj, entity):
                obj.send_entity_autoconfig()
        print("Autoconfigs has been sent...")
    else:
        print("Failed to connect, return code %d\n", rc)


#Callback
def on_message(client, userdata, message):
    print(f"Incomming Message: {message.topic}{message.payload}")
    command_json = json.loads(message.payload)
    
    if output_hardness.name in command_json:
        set_value(output_hardness, 60, command_json[output_hardness.name], 8)

    elif salt_stock.name in command_json:
        set_value(salt_stock, 94,command_json[salt_stock.name]*1000, 16)
    
    elif water_lock.name in command_json:
        set_water_lock(command_json[water_lock.name])

    elif regeneration_start.name in command_json:
        start_regeneration()

    elif sleepmode.name in command_json:
        set_sleepmode(command_json[sleepmode.name])

    elif max_waterflow.name in command_json:
        set_value(max_waterflow, 75, command_json[max_waterflow.name], 16)

    elif extraction_time.name in command_json:
        set_value(extraction_time, 74, command_json[extraction_time.name], 16)

    elif extraction_quantity.name in command_json:
        set_value(extraction_quantity, 76, command_json[extraction_quantity.name], 16)

    else:
        print("Command_Name_Error!!")


def publish_json(client, topic, message):
    json_message = json.dumps(message)
    result = client.publish(topic, json_message, qos=0, retain=True)
	
    if __debug__:
        status = result[0]
        if status == 0:
            print(f"Send `{json_message}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")


def set_water_lock(pos):
    if pos < 2:
        pos_index = str(73 - pos)
        if send_command(pos_index, ""):
            print(f"Leackage protection has been switched {pos} successfully ")
        else:
            print("HTTP Error while setting the leackage protection")
    else:
        print("Command_Error!!")


def set_sleepmode(hours):
    hours = clamp(hours,sleepmode.minimum,sleepmode.maximum)
    if hours == 0:
        if send_command("73", ""):
            print("Sleepmode has been successfully disabled, Leakage protection is active now")
        else:
            print("HTTP Error while disabling the sleepmode")
    else:
        if send_command("171", str(hours)):
            print(f"Sleepmodetime was set to {hours}h successfully")
        else:
            print("HTTP Error while setting up the sleepmode-time")

        time.sleep(2)

        if send_command("171", ""):
            print("Sleepmode has been successfully enabled, Leakage protection is disabled now")
        else:
            print("HTTP Error while enabling the sleepmode")


def start_regeneration():
    if send_command("65", ""):
        print("Regeneration has been started successfully")
    else:
        print("HTTP Error while setting the regeneration-trigger")


def set_value(obj, index, value, length):
    if send_command(str(index), int_to_le_hex(value, length)):
        print(f"{obj.name} has been set to {value} successfully")
    else:
        print(f"HTTP Error while setting {obj.name}")


def send_command(index, data):
    cmd_response = http.request('GET', f"https://www.myjudo.eu/interface/?token={my_token}&group=register&command=write%20data&serial_number={my_serial}&dt={my_dt}&index={index}&data={data}&da={my_da}&role=customer")
    cmd_response_json = json.loads(cmd_response.data)
    if "status" in cmd_response_json:
        if cmd_response_json["status"] == "ok":
            return True
    return False


def le_hex_to_int(hexstring):
    # convert little endian hex to integer
    return int.from_bytes(bytes.fromhex(hexstring), byteorder='little')

def int_to_le_hex(integer,length):
    if length == 16:
        tmp = "%0.4X" % integer
        return (tmp[2:4] + tmp[0:2])
    elif length == 8:
        return ("%0.2X" % integer)
    else:
        sys.exit("failed by int to hex conversion")

def judo_login(username, password):
    pwmd5 = hashlib.md5(password.encode("utf-8")).hexdigest()
    login_response = http.request('GET', f"https://www.myjudo.eu/interface/?group=register&command=login&name=login&user={username}&password={pwmd5}&nohash=Service&role=customer")
    login_response_json = json.loads(login_response.data)
 
    if "token" in login_response_json:
        print(f"Login successfull, got new token: {login_response_json['token']}")
        return login_response_json['token']
    else:
        sys.exit("Login to myjudo.eu failed.")

	
#INIT
command_topic =f"{config_getjudo.LOCATION}/{config_getjudo.NAME}/command"
state_topic = f"{config_getjudo.LOCATION}/{config_getjudo.NAME}/state"
availability_topic = f"{config_getjudo.LOCATION}/{config_getjudo.NAME}/status"
client_id = f"{config_getjudo.NAME}-{config_getjudo.LOCATION}"

http = urllib3.PoolManager()

my_token = judo_login(config_getjudo.JUDO_USER, config_getjudo.JUDO_PASSWORD)

next_revision = entity("Revision_in", "mdi:account-wrench", "sensor", "Tagen")
total_water = entity("Gesamtwasserverbrauch", "mdi:water", "total_increasing", "m³")
total_softwater = entity("Gesamtweichwasserverbrauch", "mdi:water-outline", "total_increasing", "m³")
salt_stock = entity("Salzvorrat", "mdi:gradient-vertical", "number", "kg", 1, 50)
salt_range = entity("Salzreichweite", "mdi:chevron-triple-right", "sensor", "Tage")
output_hardness = entity("Wunschwasserhaerte", "mdi:water-minus", "number", "°dH", 1, 15)
input_hardness = entity("Rohwasserhaerte", "mdi:water-plus", "sensor", "°dH")
water_flow = entity("Wasserdurchflussmenge", "mdi:waves-arrow-right", "sensor", "L/h")
batt_capacity = entity("Batterierestkapazitaet", "mdi:battery-50", "sensor", "%")
regenerations = entity("Anzahl_Regenerationen", "mdi:recycle-variant", "sensor")
water_lock = entity("Wasser_absperren", "mdi:pipe-valve", "switch")
regeneration_start = entity("Regeneration", "mdi:recycle-variant", "switch")
sleepmode = entity("Sleepmode", "mdi:pause-octagon", "number", "h", 0, 10)

#The maximum possible values for these settings have not been configured here. 
#For a better handling of the sliders I have limited the values. 
#If I need higher values I use the sleepmode to deactivate the leakage protection.
extraction_time = entity("max_Entnahmedauer", "mdi:clock-alert-outline", "number", "min", 10, 60, 10) #can setup to max 600min 
max_waterflow = entity("max_Wasserdurchfluss", "mdi:waves-arrow-up", "number", "L/h", 500, 2000, 500) #can setup to max 5000L/h 
extraction_quantity = entity("max_Entnahmemenge", "mdi:cup-water", "number", "L", 100, 500, 100)      #can setup to max 3000L


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
if config_getjudo.USE_MQTT_AUTH:
    client.username_pw_set(config_getjudo.MQTTUSER, config_getjudo.MQTTPASSWD)
client.will_set(availability_topic, config_getjudo.AVAILABILITY_OFFLINE, qos=0, retain=True)
client.connect(config_getjudo.BROKER, config_getjudo.PORT, 60)
client.loop_start()


#MAIN LOOP
while True:
    print("Sending GET to Cloud-Service...")
    response = http.request('GET',f"https://www.myjudo.eu/interface/?token={my_token}&group=register&command=get%20device%20data")
    response_json = json.loads(response.data)
    
    if "status" in response_json:
        if response_json["status"] ==  "ok":
            print("Parsing values from response...")
            my_serial = response_json["data"][0]["serialnumber"]
            my_da = response_json["data"][0]["data"][0]["da"]
            my_dt = response_json["data"][0]["data"][0]["dt"]

            #Next revision in days #7
            val = response_json["data"][0]["data"][0]["data"]["7"]["data"]
            next_revision.value = int(le_hex_to_int(val[0:4])/24)

            #Total Water Consumption #8
            val = response_json["data"][0]["data"][0]["data"]["8"]["data"]
            total_water.value = float(le_hex_to_int(val[0:8]))/1000

            #Total Softwater Consumption #9
            val = response_json["data"][0]["data"][0]["data"]["9"]["data"]
            total_softwater.value = float(le_hex_to_int(val[0:8]))/1000


            #Salt Stock & Salt Range #94
            val = response_json["data"][0]["data"][0]["data"]["94"]["data"]
            salt_stock.value = le_hex_to_int(val[0:4])/1000
            salt_range.value = le_hex_to_int(val[4:8])

            #Input/Output Hardness, Water flow rate #790
            val =response_json["data"][0]["data"][0]["data"]["790"]["data"] 
            output_hardness.value = int(val[18:20],16)
            input_hardness.value = int(val[54:56],16)
            input_hardness.value = float(input_hardness.value)/2 + 2            #ISSUE: Is this formular correct?
            water_flow.value = le_hex_to_int(val[34:38])

            #Regnerations #791
            val = response_json["data"][0]["data"][0]["data"]["791"]["data"]
            regenerations.value = le_hex_to_int(val[62:66])
            regeneration_start.value = int(val[3:4])
            if regeneration_start.value > 0:
                regeneration_start.value = 1

            #Battery capacity #93
            val = response_json["data"][0]["data"][0]["data"]["93"]["data"]
            batt_capacity.value = int(val[6:8],16)

            #Leakage protection valve #792
            val = response_json["data"][0]["data"][0]["data"]["792"]["data"]
            water_lock.value = int(val[2:4],16)
            if water_lock.value > 1:
                water_lock.value = 1
            sleepmode.value = int(val[20:22], 16)
            max_waterflow.value = le_hex_to_int(val[26:30])
            extraction_quantity.value = le_hex_to_int(val[30:34])
            extraction_time.value = le_hex_to_int(val[34:38])

            print("Publishing parsed values over MQTT....")
            client.publish(availability_topic, config_getjudo.AVAILABILITY_ONLINE, qos=0, retain=True)

            outp_val_dict = {}
            for obj in gc.get_objects():
                if isinstance(obj, entity):
                    outp_val_dict[obj.name] = str(obj.value)
            publish_json(client, state_topic, outp_val_dict)

        elif response_json["status"] == "error":
            if response_json["data"] == "login failed":
                print("Error: No valid Token, trying to get a new one...")
                my_token = judo_login(config_getjudo.JUDO_USER, config_getjudo.JUDO_PASSWORD)
            else:
                val = response_json["data"]
                print(f"Response Error: {val}")
        else:
            sys.exit("Error: Unspecific response status")
    else:
        sys.exit("Error: Invalid response")

    print("Spend some time....")
    time.sleep(config_getjudo.STATE_UPDATE_INTERVAL)

