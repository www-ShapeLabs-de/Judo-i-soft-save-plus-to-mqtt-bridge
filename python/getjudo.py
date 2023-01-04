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
    def __init__(self, name, icon, entity_type, unit = "", minimum = 1, maximum = 100, value = 0):
        self.name = name
        self.unit = unit
        self.icon = icon
        self.entity_type = entity_type #total_inc, sensor, number, switch, 
        self.value = value
        self.minimum = minimum
        self.maximum = maximum

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
        set_outp_hardness(command_json[output_hardness.name])
    
    elif salt_stock.name in command_json:
        set_salt_stock(command_json[salt_stock.name])
    
    elif water_lock.name in command_json:
        set_water_lock(command_json[water_lock.name])
    
    elif start_regeneration.name in command_json:
        set_water_lock(command_json[start_regeneration.name])

    else:
        print("Command_Name_Error!!")


def publish_json(client, topic, message):
    json_message = json.dumps(message)
    result = client.publish(topic, json_message)
    if __debug__:
        status = result[0]
        if status == 0:
            print(f"Send `{json_message}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")


def set_outp_hardness(hardness):
    hardness = clamp(hardness, output_hardness.minimum, output_hardness.maximum)
    hardness_str = "%0.2X" % hardness
    if send_command("60", hardness_str):
        print(f"Output_hardness was successfully set to {str(hardness)}°dH")
    else:
        print("HTTP Error while setting the output_hardness")


def set_water_lock(pos):
    if pos < 2:
        pos_index = str(73 - pos)
        if send_command(pos_index, ""):
            print(f"Leackage protection has been switched {pos} successfully ")
        else:
            print("HTTP Error while setting the leackage protection")
    else:
        print("Command_Error!!")


def set_salt_stock(mass): #0-50kg
    mass = clamp(mass, salt_stock.minimum, salt_stock.maximum)
    mass_str = "%0.4X" % (mass*1000)
    mass_str = mass_str[2:4] + mass_str[0:2]
    if send_command("94", mass_str):
        print(f"Saltlevel set to {str(mass)}kg successfully")
    else:
        print("HTTP Error while setting the salt level")


def start_regeneration():
    if send_command("65", ""):
        print("Regeneration has been started successfully")
    else:
        print("HTTP Error while setting the regeneration-trigger")


def send_command(index, data):
    cmd_response = http.request('GET', f"https://www.myjudo.eu/interface/?token={my_token}&group=register&command=write%20data&serial_number={my_serial}&dt={my_dt}&index={index}&data={data}&da={my_da}&role=customer")
    cmd_response_json = json.loads(cmd_response.data)
    if "status" in cmd_response_json:
        if cmd_response_json["status"] == "ok":
            return True
    return False


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


def le_hex_to_int(hexstring):
    # convert little endian hex to integer
    return int.from_bytes(bytes.fromhex(hexstring), byteorder='little')


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
water_lock = entity("Leckageschutz", "mdi:pipe-valve", "switch")
regeneration_start = entity("Regeneration", "mdi:recycle-variant", "switch")


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
            input_hardness.value = float(input_hardness.value)/2 + 2
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

            print("Publishing parsed values over MQTT....")
            client.publish(availability_topic, config_getjudo.AVAILABILITY_ONLINE, qos=0, retain=True)

            outp_val_dict = {}
            for obj in gc.get_objects():
                if isinstance(obj, entity):
                    outp_val_dict[obj.name] = str(obj.value)
            #publish_json(client, state_topic, outp_val_dict)

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

