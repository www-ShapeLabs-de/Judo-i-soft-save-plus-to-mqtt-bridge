#!/urs/bin/python3

import urllib3
import json
import time
import getjudo_config.py
from paho.mqtt import client as mqtt

class entity():
    def __init__(self, name, unit, icon, entity_type, value):
        self.name = name
        self.unit = unit
        self.icon = icon
        self.entity_type = entity_type #total_inc, sensor, number, switch, 
        self.value = value

    def send_entity_autoconfig(self):
        device_config = {
            "identifiers": f"[{client_id}]",
            "manufacturer": MANUFACTURER,
            "model": NAME,
            "name": client_id,
            "sw_version": SW_VERSION
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
            entity_config["unit_of_measurement"] = self.unit;

        elif self.entity_type == "number":
            entity_config["command_topic"] = command_topic
            entity_config["unit_of_measurement"] = self.unit
            entity_config["min"] = "1"
            entity_config["max"] = "15"
            entity_config["command_template"] = "{\"" + self.name + "\": {{ value }}}"

        elif self.entity_type == "switch":
            entity_config["command_topic"] = command_topic
            entity_config["payload_on"] = "{\"" + self.name + "\": \"on\"}"
            entity_config["payload_off"] = "{\"" + self.name + "\": \"off\"}"
            entity_config["state_on"] = "on"
            entity_config["state_off"] = "off"

        elif self.entity_type == "sensor":
            entity_config["unit_of_measurement"] = self.unit;

        else:
            print ("autoconf ERROR!!")

        autoconf_topic = f"homeassistant/{self.entity_type}/{LOCATION}/{NAME}_{self.name}/config"
        
        publish_json(client, autoconf_topic, entity_config)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker...")
        client.subscribe(command_topic)
        print("Subscribing Topics...")
        total_water.send_entity_autoconfig()
        total_softwater.send_entity_autoconfig()
        salt_stock.send_entity_autoconfig()
        salt_range.send_entity_autoconfig()
        output_hardness.send_entity_autoconfig()
        input_hardness.send_entity_autoconfig()
        water_flow.send_entity_autoconfig()
        batt_capacity.send_entity_autoconfig()
        regenerations.send_entity_autoconfig()
        water_lock.send_entity_autoconfig()
        print("Sending Autoconfigs...")

        client.publish(availability_topic, AVAILABILITY_ONLINE)
    else:
        print("Failed to connect, return code %d\n", rc)

#Callback
def on_message(client, userdata, message):
    print(f"Incomming Message: {message.topic}{message.payload}")
    command_json = json.loads(message.payload)
    if output_hardness.name in command_json:
        set_outp_hardness(command_json[output_hardness.name])
    elif water_lock.name in command_json:
        set_water_lock(command_json[water_lock.name])
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
    if hardness < 1:
        hardness = 1
    elif hardness >15:
        hardness = 15

    hex_str = hex(hardness)[2:]

    cmd_response = http.request('GET',f"https://www.myjudo.eu/interface/?token={TOKEN}&group=register&command=write%20data&serial_number={SERIAL}&dt=0x33&index=60&data=0{hex_str}&da=0x1&role=customer&action=normal")
    cmd_response_json = json.loads(cmd_response.data)

    if cmd_response_json["status"] == "ok":
        print(f"Output_hardness was successfully set to {str(hardness)}°dH")
    else:
        print("HTTP Error while setting the output_hardness")

def set_water_lock(pos)
    if pos == "off" or pos == "on":
        if pos == "on":
            pos_code = "72"
        elif pos == "off"
            pos_code = "73"

        cmd_response = http.request('GET', f"https://www.myjudo.eu/interface/?token={TOKEN}&group=register&command=write%20data&serial_number={SERIAL})&dt=0x33&index={pos_code}&data=&da=0x1&role=customer")

        if cmd_response_json["status"] == "ok":
            print(f"Leackage protection has been switched {pos} successfully ")
        else:
            print("HTTP Error while setting the leackage protection")
    else:
        print("Command_Error!!")

#INIT
command_topic =f"{LOCATION}/{NAME}/command"
state_topic = f"{LOCATION}/{NAME}/state"
availability_topic = f"{LOCATION}/{NAME}/status"
client_id = f"{NAME}-{LOCATION}"

http = urllib3.PoolManager()

total_water = entity("Gesamtwasserverbrauch", "m³","mdi:water", "total_increasing", 0)
total_softwater = entity("Gesamtweichwasserverbrauch", "m³","mdi:water-outline", "total_increasing", 0)
salt_stock = entity("Salzvorrat", "g", "mdi:gradient-vertical", "sensor", 0)
salt_range = entity("Salzreichweite", "Tage", "mdi:chevron-triple-right", "sensor", 0)
output_hardness = entity("Wunschwasserhaerte", "°dH", "mdi:water-minus", "number", 0)
input_hardness = entity("Rohwasserhaerte", "°dH", "mdi:water-plus", "sensor", 0)
water_flow = entity("Wasserdurchflussmenge", "L/h", "mdi:waves-arrow-right", "sensor", 0)
batt_capacity = entity("Batterierestkapazität", "%", "mdi:battery-50", "sensor", 0)
regenerations = entity("Regenerationen", " ", "mdi:recycle-variant", "sensor", 0)
water_lock = entity("Leckageschutz", " ", "mdi:pipe-valve", "switch", 0)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(MQTTUSER, MQTTPASSWD)
client.connect(BROKER, PORT, 60)
client.loop_start()

#MAIN LOOP
while True:
    print("Sending GET to Cloud-Service...")
    response = http.request('GET',f"https://www.myjudo.eu/interface/?token={TOKEN}&group=register&command=get%20device%20data")
    response_json = json.loads(response.data)

    #Total Water Consumption #8
    val = response_json["data"][0]["data"][0]["data"]["8"]["data"]
    total_water.value = int((val[6:8] + val[4:6] + val[2:4] + val[0:2]),16)
    total_water.value = float(total_water.value)/1000

    #Total Softwater Consumption #9
    val = response_json["data"][0]["data"][0]["data"]["9"]["data"]
    total_softwater.value = int((val[6:8] + val[4:6] + val[2:4] + val[0:2]),16)
    total_softwater.value = float(total_softwater.value)/1000

    #Salt Stock & Salt Range #94
    val = response_json["data"][0]["data"][0]["data"]["94"]["data"]
    salt_stock.value = int((val[2:4] + val[0:2]),16)
    salt_range.value = int((val[6:8] + val[4:6]),16)

    #Input/Output Hardness, Durchflussmenge #790
    val =response_json["data"][0]["data"][0]["data"]["790"]["data"] 
    output_hardness.value = int(val[18:20],16)
    input_hardness.value = int(val[54:56],16)
    input_hardness.value = float(input_hardness.value)/2 + 2
    water_flow.value = int((val[36:38] + val[34:36]),16)

    #Regnerationen #791
    val = response_json["data"][0]["data"][0]["data"]["791"]["data"]
    regenerations.value = int((val[64:66] + val[62:64]),16)

    #Batteriekapazitaet #93
    val = response_json["data"][0]["data"][0]["data"]["93"]["data"]
    batt_capacity.value = int(val[6:8],16)

    #Leckageschutz #792
    val = response_json["data"][0]["data"][0]["data"]["792"]["data"]
    water_lock.value = int(val[2:4],16)
    if water_lock.value:
        water_lock.value = "on"
    else:
        water_lock.value = "off"


    outp_val_dict = {
        total_water.name: str(total_water.value),
        total_softwater.name: str(total_softwater.value),
        salt_stock.name: str(salt_stock.value),
        salt_range.name: str(salt_range.value),
        output_hardness.name: str(output_hardness.value),
        input_hardness.name: str(input_hardness.value),
        water_flow.name: str(water_flow.value),
        regenerations.name: str(regenerations.value),
        batt_capacity.name: str(batt_capacity.value),
        water_lock.name: water_lock.value
    }
    print("Publishing values over MQTT....")
    publish_json(client, state_topic, outp_val_dict)

    time.sleep(STATE_UPDATE_INTERVAL)


