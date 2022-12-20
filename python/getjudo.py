#!/urs/bin/python3
# -*- coding: utf-8 -*-

import urllib3
import json
import time
import gc
import config_getjudo
from paho.mqtt import client as mqtt

class entity():
    def __init__(self, name, unit, icon, entity_type, value, minimum, maximum):
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
            entity_config["min"] = str(self.minimum)
            entity_config["max"] = str(self.maximum)
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
        
        client.publish(availability_topic, config_getjudo.AVAILABILITY_ONLINE)

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
    if hardness < 1:
        hardness = 1
    elif hardness > 15:
        hardness = 15

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
    if mass > 50:
        mass = 50
    elif mass < 0:
        mass = 0
    mass_str = "%0.4X" % (mass*1000)
    mass_str = mass_str[2:4] + mass_str[0:2]
    if send_command("94",mass_str):
        print(f"Saltlevel set to {str(mass)}kg successfully")
    else:
        print("HTTP Error while setting the salt level")


def start_regeneration():
    if send_command("65", ""):
        print("Regeneration has been started successfully")
    else:
        print("HTTP Error while setting the regeneration-trigger")


def send_command(index, data):
    cmd_response = http.request('GET', f"https://www.myjudo.eu/interface/?token={config_getjudo.TOKEN}&group=register&command=write%20data&serial_number={my_serial}&dt={my_dt}&index={index}&data={data}&da={my_da}&role=customer")
    cmd_response_json = json.loads(cmd_response.data)
    if "status" in cmd_response_json:
        if cmd_response_json["status"] == "ok":
            return True
    return False

	
#INIT
command_topic =f"{config_getjudo.LOCATION}/{config_getjudo.NAME}/command"
state_topic = f"{config_getjudo.LOCATION}/{config_getjudo.NAME}/state"
availability_topic = f"{config_getjudo.LOCATION}/{config_getjudo.NAME}/status"
client_id = f"{config_getjudo.NAME}-{config_getjudo.LOCATION}"

http = urllib3.PoolManager()

next_revision = entity("Revision in", "Tagen", "mdi:account-wrench", "sensor", 0,0,0)
total_water = entity("Gesamtwasserverbrauch", "m³","mdi:water", "total_increasing", 0,0,0)
total_softwater = entity("Gesamtweichwasserverbrauch", "m³","mdi:water-outline", "total_increasing", 0,0,0)
salt_stock = entity("Salzvorrat", "kg", "mdi:gradient-vertical", "number", 0, 1, 50)
salt_range = entity("Salzreichweite", "Tage", "mdi:chevron-triple-right", "sensor", 0,0,0)
output_hardness = entity("Wunschwasserhaerte", "°dH", "mdi:water-minus", "number", 0, 1, 15)
input_hardness = entity("Rohwasserhaerte", "°dH", "mdi:water-plus", "sensor", 0,0,0)
water_flow = entity("Wasserdurchflussmenge", "L/h", "mdi:waves-arrow-right", "sensor", 0,0,0)
batt_capacity = entity("Batterierestkapazitaet", "%", "mdi:battery-50", "sensor", 0,0,0)
regenerations = entity("Anzahl_Regenerationen", " ", "mdi:recycle-variant", "sensor", 0,0,0)
water_lock = entity("Leckageschutz", " ", "mdi:pipe-valve", "switch", 0,0,0)
regeneration_start = entity("Regeneration", " ", "mdi:recycle-variant", "switch", 0 ,0, 0)
#= entity_type("", "", "", "", 0 ,0, 0) #Name, Unit, Icon, Type, Initial Value, Min, Max 

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
if config_getjudo.USE_MQTT_AUTH:
    client.username_pw_set(config_getjudo.MQTTUSER, config_getjudo.MQTTPASSWD)
client.connect(config_getjudo.BROKER, config_getjudo.PORT, 60)
client.loop_start()

#MAIN LOOP
while True:
    print("Sending GET to Cloud-Service...")
    response = http.request('GET',f"https://www.myjudo.eu/interface/?token={config_getjudo.TOKEN}&group=register&command=get%20device%20data")
    response_json = json.loads(response.data)

    print("Parsing values from response...")
    my_serial = response_json["data"][0]["serialnumber"]
    my_da = response_json["data"][0]["data"][0]["da"]
    my_dt = response_json["data"][0]["data"][0]["dt"]


    #Next revision in days #7
    val = response_json["data"][0]["data"][0]["data"]["7"]["data"]
    next_revision.value = int(int(val[2:4] + val[0:2],16)/24)

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
    salt_stock.value = int((val[2:4] + val[0:2]),16)/1000
    salt_range.value = int((val[6:8] + val[4:6]),16)

    #Input/Output Hardness, Water flow rate #790
    val =response_json["data"][0]["data"][0]["data"]["790"]["data"] 
    output_hardness.value = int(val[18:20],16)
    input_hardness.value = int(val[54:56],16)
    input_hardness.value = float(input_hardness.value)/2 + 2
    water_flow.value = int((val[36:38] + val[34:36]),16)

    #Regnerations #791
    val = response_json["data"][0]["data"][0]["data"]["791"]["data"]
    regenerations.value = int((val[64:66] + val[62:64]),16)
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
    outp_val_dict = {}
    for obj in gc.get_objects():
        if isinstance(obj, entity):
            outp_val_dict[obj.name] = str(obj.value)
    publish_json(client, state_topic, outp_val_dict)

    print("Spend some time....")
    time.sleep(config_getjudo.STATE_UPDATE_INTERVAL)

