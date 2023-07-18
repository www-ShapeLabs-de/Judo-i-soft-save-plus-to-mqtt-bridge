#!/usr/bin/python3
# -*- coding: utf-8 -*-
import urllib3
import json
import time
import gc
import os
import sys
import config_getjudo
import messages_getjudo
import hashlib
import math
from paho.mqtt import client as mqtt
from datetime import date
import pickle
from threading import Timer
from dataclasses import dataclass

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
            "payload_available": config_getjudo.AVAILABILITY_ONLINE,
            "payload_not_available": config_getjudo.AVAILABILITY_OFFLINE,
            "state_topic": state_topic,
            "name": client_id + " " + self.name,
            "unique_id": client_id + "_" + self.name,
            "icon": self.icon,
            "value_template": "{{value_json." + self.name + "}}"
        }

        if self.entity_type == "total_increasing":
            entity_config["device_class"] = "water"
            entity_config["state_class"] = "total_increasing"
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

        elif self.entity_type == "select":
            entity_config["command_topic"] = command_topic
            entity_config["command_template"] = "{\"" + self.name + "\": \"{{ value }}\"}"
            entity_config["options"] = self.unit

        else:
            print(messages_getjudo.debug[26])
            return

        autoconf_topic = f"homeassistant/{self.entity_type}/{config_getjudo.LOCATION}/{config_getjudo.NAME}_{self.name}/config"
        publish_json(client, autoconf_topic, entity_config)

    def parse(self, response, index, a,b):
        val = response["data"][0]["data"][0]["data"][str(index)]["data"]
        if val != "":
            self.value = int.from_bytes(bytes.fromhex(val[a:b]), byteorder='little')

class notification_entity():
    def __init__(self, name, icon, counter=0, value = ""):
        self.name = name
        self.icon = icon
        self.value = value
        self.counter = counter

    def send_autoconfig(self):
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
            "payload_available": config_getjudo.AVAILABILITY_ONLINE,
            "payload_not_available": config_getjudo.AVAILABILITY_OFFLINE,
            "state_topic": notification_topic,
            "name": client_id + " " + self.name,
            "unique_id": client_id + "_" + self.name,
            "icon": self.icon
        }
        autoconf_topic = f"homeassistant/sensor/{config_getjudo.LOCATION}/{config_getjudo.NAME}_{self.name}/config"
        publish_json(client, autoconf_topic, entity_config)

    def publish(self, message, debuglevel):
        self.value = message
        msg = str(self.value)
        print(msg)
        if config_getjudo.MQTT_DEBUG_LEVEL  >= debuglevel:
            client.publish(notification_topic, msg, qos=0, retain=True)

class Function_Caller(Timer):
    def run(self):
        while not self.finished.wait(self.interval):  
            self.function()

@dataclass
class savedata:
    day_today = 0
    offset_total_water = 0
    last_err_id = 0
    token = 0
    water_yesterday = 0
    da = 0
    dt = 0
    serial = 0
    reg_mean_time = 0
    reg_mean_counter = 1
    reg_last_val = 0
    reg_last_timestamp = 0
    total_softwater_at_reg = 0
    total_hardwater_at_reg = 0


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(messages_getjudo.debug[1])
        client.subscribe(command_topic)
        print(messages_getjudo.debug[2])
        
        client.publish(availability_topic, config_getjudo.AVAILABILITY_ONLINE, qos=0, retain=True)

        for obj in gc.get_objects():
            if isinstance(obj, entity):
                obj.send_entity_autoconfig()
        notify.send_autoconfig()
        print(messages_getjudo.debug[3])
    else:
        print(messages_getjudo.debug[4].format(rc))


#Callback
def on_message(client, userdata, message):
    print(messages_getjudo.debug[5].format(message.topic, message.payload))
    try:
        command_json = json.loads(message.payload)
        
        if output_hardness.name in command_json:
            if config_getjudo.USE_SODIUM_CHECK == True:
                sodium = round(((input_hardness.value - command_json[output_hardness.name]) * 8.2) + config_getjudo.SODIUM_INPUT,1)
                if  sodium < config_getjudo.SODIUM_LIMIT:
                    if send_command(str(60), int_to_le_hex(command_json[output_hardness.name], 8)):
                        notify.publish(messages_getjudo.debug[43].format(sodium, config_getjudo.SODIUM_LIMIT, command_json[output_hardness.name]), 2)
                else:
                    limited_hardness = input_hardness.value - ((config_getjudo.SODIUM_LIMIT - config_getjudo.SODIUM_INPUT)/8.2)
                    limited_hardness = math.ceil(limited_hardness) #round up
                    if send_command(str(60), int_to_le_hex(limited_hardness, 8)):
                        notify.publish(messages_getjudo.debug[44].format(limited_hardness), 2)
            else:
                set_value(output_hardness, 60, command_json[output_hardness.name], 8)
        elif regeneration_start.name in command_json:
                start_regeneration()


        if config_getjudo.USE_WITH_SOFTWELL_P == False:
            if salt_stock.name in command_json:
                set_value(salt_stock, 94,command_json[salt_stock.name]*1000, 16)
            
            elif water_lock.name in command_json:
                set_water_lock(command_json[water_lock.name])


            elif sleepmode.name in command_json:
                set_sleepmode(command_json[sleepmode.name])

            elif max_waterflow.name in command_json:
                set_value(max_waterflow, 75, command_json[max_waterflow.name], 16)

            elif extraction_time.name in command_json:
                set_value(extraction_time, 74, command_json[extraction_time.name], 16)

            elif extraction_quantity.name in command_json:
                set_value(extraction_quantity, 76, command_json[extraction_quantity.name], 16)

            elif holidaymode.name in command_json:
                set_holidaymode(command_json[holidaymode.name])

    except Exception as e:
        notify.publish([messages_getjudo.debug[27].format(sys.exc_info()[-1].tb_lineno),e], 3)


def publish_json(client, topic, message):
    json_message = json.dumps(message)
    result = client.publish(topic, json_message, qos=0, retain=True)


def set_water_lock(pos):
    if pos < 2:
        pos_index = str(73 - pos)
        if send_command(pos_index, ""):
            notify.publish(messages_getjudo.debug[7].format(pos), 2)
    else:
        print(messages_getjudo.debug[9])


def set_sleepmode(hours):
    if hours == 0:
        if send_command("73", ""):
            notify.publish(messages_getjudo.debug[10], 2)
    else:
        if send_command("171", str(hours)):
            notify.publish(messages_getjudo.debug[12].format(hours), 2)
        if send_command("171", ""):
            notify.publish(messages_getjudo.debug[14], 2)


def set_holidaymode(mode):
    if mode == messages_getjudo.holiday_options[1]:      #lock
        send_command("77", "9")
    elif mode == messages_getjudo.holiday_options[2]:    #mode1
        send_command("77", "3")
    elif mode == messages_getjudo.holiday_options[3]:    #mode2
        send_command("77", "5")
    else:                                               #off
        if send_command("73", ""):
            notify.publish(messages_getjudo.debug[40], 1)
        send_command("77", "0")


def start_regeneration():
    if send_command("65", ""):
        notify.publish(messages_getjudo.debug[16], 2)


def set_value(obj, index, value, length):
    if send_command(str(index), int_to_le_hex(value, length)):
        notify.publish(messages_getjudo.debug[18].format(obj.name, value), 2)


def send_command(index, data):
    try:
        cmd_response = http.request('GET', f"https://www.myjudo.eu/interface/?token={mydata.token}&group=register&command=write%20data&serial_number={mydata.serial}&dt={mydata.dt}&index={index}&data={data}&da={mydata.da}&role=customer")
        cmd_response_json = json.loads(cmd_response.data)
        if "status" in cmd_response_json:
            if cmd_response_json["status"] == "ok":
                return True
    except Exception as e:
        notify.publish([messages_getjudo.debug[27].format(sys.exc_info()[-1].tb_lineno),e], 3)
        return False
    return False


def int_to_le_hex(integer,length):
    if length == 16:
        tmp = "%0.4X" % integer
        return (tmp[2:4] + tmp[0:2])
    elif length == 8:
        return ("%0.2X" % integer)
    else:
        notify.publish(messages_getjudo.debug[20], 3)


def judo_login(username, password):
    pwmd5 = hashlib.md5(password.encode("utf-8")).hexdigest()
    try:
        login_response = http.request('GET', f"https://www.myjudo.eu/interface/?group=register&command=login&name=login&user={username}&password={pwmd5}&nohash=Service&role=customer")
        login_response_json = json.loads(login_response.data)
        if "token" in login_response_json:
            print(messages_getjudo.debug[22].format(login_response_json['token']))
            return login_response_json['token']
        else:
            notify.publish(messages_getjudo.debug[21], 2)
            sys.exit()
    except Exception as e:
        notify.publish([messages_getjudo.debug[28].format(sys.exc_info()[-1].tb_lineno),e], 3)
        sys.exit()


#----- INIT ----
command_topic =f"{config_getjudo.LOCATION}/{config_getjudo.NAME}/command"
state_topic = f"{config_getjudo.LOCATION}/{config_getjudo.NAME}/state"
availability_topic = f"{config_getjudo.LOCATION}/{config_getjudo.NAME}/status"
notification_topic = f"{config_getjudo.LOCATION}/{config_getjudo.NAME}/notify"
client_id = f"{config_getjudo.NAME}-{config_getjudo.LOCATION}"

http = urllib3.PoolManager()
mydata = savedata()


#Setting up all entities for homeassistant
next_revision = entity(messages_getjudo.entities[0], "mdi:account-wrench", "sensor", "Tagen")
total_water = entity(messages_getjudo.entities[1], "mdi:water-circle", "total_increasing", "m³")
output_hardness = entity(messages_getjudo.entities[6], "mdi:water-minus", "number", "°dH", 1, 15)
input_hardness = entity(messages_getjudo.entities[7], "mdi:water-plus", "sensor", "°dH")
regenerations = entity(messages_getjudo.entities[10], "mdi:water-sync", "sensor")
regeneration_start = entity(messages_getjudo.entities[12], "mdi:recycle-variant", "switch")
water_today = entity(messages_getjudo.entities[14], "mdi:chart-box", "sensor", "L")
water_yesterday = entity(messages_getjudo.entities[15], "mdi:chart-box-outline", "sensor", "L")
notify = notification_entity(messages_getjudo.entities[16], "mdi:alert-outline")
h_since_last_reg = entity(messages_getjudo.entities[21], "mdi:water-sync", "sensor", "h")
avg_reg_interval = entity(messages_getjudo.entities[22], "mdi:water-sync", "sensor", "h")


if config_getjudo.USE_WITH_SOFTWELL_P == False:
    salt_stock = entity(messages_getjudo.entities[4], "mdi:gradient-vertical", "number", "kg", 1, 50)
    salt_range = entity(messages_getjudo.entities[5], "mdi:chevron-triple-right", "sensor", "Tage")
    total_softwater_proportion = entity(messages_getjudo.entities[2], "mdi:water-outline", "total_increasing", "m³")
    total_hardwater_proportion = entity(messages_getjudo.entities[3], "mdi:water", "total_increasing", "m³")
    water_flow = entity(messages_getjudo.entities[8], "mdi:waves-arrow-right", "sensor", "L/h")
    batt_capacity = entity(messages_getjudo.entities[9], "mdi:battery-50", "sensor", "%")
    water_lock = entity(messages_getjudo.entities[11], "mdi:pipe-valve", "switch")
    sleepmode = entity(messages_getjudo.entities[13], "mdi:pause-octagon", "number", "h", 0, 10)
    extraction_time = entity(messages_getjudo.entities[17], "mdi:clock-alert-outline", "number", "min", 10, config_getjudo.LIMIT_EXTRACTION_TIME, 10)
    max_waterflow = entity(messages_getjudo.entities[18], "mdi:waves-arrow-up", "number", "L/h", 500, config_getjudo.LIMIT_MAX_WATERFLOW, 500)
    extraction_quantity = entity(messages_getjudo.entities[19], "mdi:cup-water", "number", "L", 100, config_getjudo.LIMIT_EXTRACTION_QUANTITY, 100)
    holidaymode = entity(messages_getjudo.entities[20], "mdi:palm-tree", "select", messages_getjudo.holiday_options)
    mixratio = entity(messages_getjudo.entities[23], "mdi:tune-vertical", "sensor", "L")

try: 
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    if config_getjudo.USE_MQTT_AUTH:
        client.username_pw_set(config_getjudo.MQTTUSER, config_getjudo.MQTTPASSWD)
    client.will_set(availability_topic, config_getjudo.AVAILABILITY_OFFLINE, qos=0, retain=True)
    client.connect(config_getjudo.BROKER, config_getjudo.PORT, 60)
    client.loop_start()
except Exception as e:
    sys.exit(messages_getjudo.debug[33])


#Load stored variables:
print (messages_getjudo.debug[34])
print ("----------------------")
try:
    with open(config_getjudo.TEMP_FILE,"rb") as temp_file:
        mydata = pickle.load(temp_file)
    print (messages_getjudo.debug[35].format(mydata.last_err_id))
    print (messages_getjudo.debug[36].format(mydata.water_yesterday))
    water_yesterday.value = mydata.water_yesterday
    print (messages_getjudo.debug[37].format(mydata.offset_total_water))
    print (messages_getjudo.debug[38].format(mydata.day_today))
    print ("da: {}".format(mydata.da))
    print ("dt: {}".format(mydata.dt))
    print ("serial: {}".format(mydata.serial))
    print ("token: {}".format(mydata.token))
    print ("avergage regeneration interval: {}h".format(mydata.reg_mean_time))
    print ("counter for avg-calc: {}".format(mydata.reg_mean_counter))
    print ("last regenerations count: {}".format(mydata.reg_last_val))
    print ("timestamp of last regeneration: {}s".format(mydata.reg_last_timestamp))
    if config_getjudo.USE_WITH_SOFTWELL_P == False:
        print ("Softwater prop. since Regeneration: {}L".format(mydata.total_softwater_at_reg))
        print ("Hardwater prop. since Regeneration: {}L".format(mydata.total_hardwater_at_reg))

except Exception as e:
    notify.publish([messages_getjudo.debug[29].format(sys.exc_info()[-1].tb_lineno),e], 3)
    try:
        with open(config_getjudo.TEMP_FILE,"wb") as temp_file:
            pickle.dump(mydata, temp_file)
        notify.publish(messages_getjudo.debug[41], 3)
    except:
        notify.publish([messages_getjudo.debug[42].format(sys.exc_info()[-1].tb_lineno),e], 3)
        sys.exit()

if mydata.token == 0:
    mydata.token = judo_login(config_getjudo.JUDO_USER, config_getjudo.JUDO_PASSWORD)


avg_reg_interval.value = mydata.reg_mean_time


#----- Mainthread ----
def main():
    try:
        response = http.request('GET',f"https://www.myjudo.eu/interface/?token={mydata.token}&group=register&command=get%20device%20data")
        response_json = json.loads(response.data)
        if response_json["status"] ==  "ok":
            #print("Parsing values from response...")
            mydata.serial = response_json["data"][0]["serialnumber"]
            mydata.da = response_json["data"][0]["data"][0]["da"]
            mydata.dt = response_json["data"][0]["data"][0]["dt"]

            next_revision.parse(response_json, 7, 0, 4)
            if config_getjudo.USE_WITH_SOFTWELL_P == False:
                total_water.parse(response_json, 8, 0, 8)
                salt_stock.parse(response_json,94, 0, 4)
                salt_range.parse(response_json,94, 4, 8)
                total_softwater_proportion.parse(response_json, 9, 0, 8)
                water_flow.parse(response_json, 790, 34, 38)
                batt_capacity.parse(response_json, 93, 6, 8)
                water_lock.parse(response_json, 792, 2, 4)
                sleepmode.parse(response_json,792, 20, 22)
                max_waterflow.parse(response_json, 792, 26, 30)
                extraction_quantity.parse(response_json, 792, 30, 34)
                extraction_time.parse(response_json, 792, 34, 38)
                holidaymode.parse(response_json,792, 38, 40)
            else:
                total_water.parse(response_json, 9, 0, 8)

            output_hardness.parse(response_json, 790, 18, 20)
            input_hardness.parse(response_json, 790, 54, 56)
            regenerations.parse(response_json, 791, 62, 66)
            regeneration_start.parse(response_json, 791, 2, 4)

            next_revision.value = int(next_revision.value/24)   #Calculation hours to days
            total_water.value =float(total_water.value/1000) # Calculating from L to m³

            if config_getjudo.USE_WITH_SOFTWELL_P == False:
                if holidaymode.value == 3:      #mode1
                    holidaymode.value = messages_getjudo.holiday_options[2]
                elif holidaymode.value == 5:    #mode2
                    holidaymode.value = messages_getjudo.holiday_options[3]
                elif holidaymode.value == 9:    #lock
                    holidaymode.value = messages_getjudo.holiday_options[1]
                else:                           #off
                    holidaymode.value = messages_getjudo.holiday_options[0]

                total_softwater_proportion.value = float(total_softwater_proportion.value/1000)# Calculating from L to m³
                total_hardwater_proportion.value = round((total_water.value - total_softwater_proportion.value),3)
                salt_stock.value /= 1000 
                if water_lock.value > 1:
                    water_lock.value = 1

            regeneration_start.value &= 0x0F
            if regeneration_start.value > 0:
                regeneration_start.value = 1


            today = date.today()
            #It's 12pm...a new day. Store today's value to yesterday's value and setting a new offset for a new count
            if today.day != mydata.day_today:
                mydata.day_today = today.day
                mydata.offset_total_water = int(1000*total_water.value)
                water_yesterday.value = water_today.value
                mydata.water_yesterday = water_today.value
            water_today.value = int(1000*total_water.value) - mydata.offset_total_water

            #Hours since last regeneration / Average regeneration interval
            if regenerations.value > mydata.reg_last_val:
                if (regenerations.value - mydata.reg_last_val) == 1: #Regeneration has started, 
                    if mydata.reg_last_timestamp != 0:
                        h_since_last_reg.value = math.ceil((int(time.time()) - mydata.reg_last_timestamp)/3600)
                        #neuer_mittelwert = ((counter-1)*alter_mittelwert + neuer_wert)/counter
                        avg_reg_interval.value = math.ceil(((mydata.reg_mean_counter-1)*mydata.reg_mean_time + h_since_last_reg.value)/mydata.reg_mean_counter)
                        mydata.reg_mean_time = avg_reg_interval.value
                        mydata.reg_mean_counter += 1
                    mydata.reg_last_timestamp = int(time.time()) 
                    mydata.reg_last_val = regenerations.value
                    if config_getjudo.USE_WITH_SOFTWELL_P == False:
                        mydata.total_softwater_at_reg = total_softwater_proportion.value
                        mydata.total_hardwater_at_reg = total_hardwater_proportion.value
                else:
                    mydata.reg_last_val = regenerations.value
            if mydata.reg_last_timestamp != 0:
                h_since_last_reg.value = int((int(time.time()) - mydata.reg_last_timestamp)/3600)

            #Mix ratio Soft:Hard since last regeneration
            if config_getjudo.USE_WITH_SOFTWELL_P == False:
                softwater_since_reg = total_softwater_proportion.value - mydata.total_softwater_at_reg
                hardwater_since_reg = total_hardwater_proportion.value - mydata.total_hardwater_at_reg
                if softwater_since_reg != 0 and hardwater_since_reg !=0:
                    totalwater_since_reg = softwater_since_reg +  hardwater_since_reg

                    if hardwater_since_reg < softwater_since_reg:
                        mixratio.value = "1:" + str(round(1/(hardwater_since_reg/totalwater_since_reg),2))
                    else:
                        mixratio.value = str(round(1/(softwater_since_reg/totalwater_since_reg),2)) + ":1"
                else:
                    mixratio.value = "unknown"


            #print("Publishing parsed values over MQTT....")
            outp_val_dict = {}
            for obj in gc.get_objects():
                if isinstance(obj, entity):
                    outp_val_dict[obj.name] = str(obj.value)
            publish_json(client, state_topic, outp_val_dict)

        elif response_json["status"] == "error":
            notify.counter += 1
            if response_json["data"] == "login failed":
                notify.publish(messages_getjudo.debug[23],3)
                mydata.token = judo_login(config_getjudo.JUDO_USER, config_getjudo.JUDO_PASSWORD)
            else:
                val = response_json["data"]
                notify.publish(messages_getjudo.debug[24].format(val),3)
                notify.counter += 1
        else:
            print(messages_getjudo.debug[25])
            notify.counter += 1
    except Exception as e:
        notify.publish([messages_getjudo.debug[31].format(sys.exc_info()[-1].tb_lineno),e],3)
        notify.counter += 1

    try:
        error_response = http.request('GET',f"https://myjudo.eu/interface/?token={mydata.token}&group=register&command=get%20error%20messages")
        error_response_json = json.loads(error_response.data)
        if error_response_json["data"] != [] and error_response_json["count"] != 0:
            if mydata.last_err_id != error_response_json["data"][0]["id"]:
                mydata.last_err_id = error_response_json["data"][0]["id"]

                timestamp = error_response_json["data"][0]["ts_sort"]
                timestamp = timestamp[:-7] + ": "

                if error_response_json["data"][0]["type"] == "w":
                    error_message = timestamp + messages_getjudo.warnings[error_response_json["data"][0]["error"]]
                    notify.publish(error_message, 1)
                elif error_response_json["data"][0]["type"] == "e":
                    error_message = timestamp + messages_getjudo.errors[error_response_json["data"][0]["error"]]
                    notify.publish(error_message, 1)
    except Exception as e:
        notify.publish([messages_getjudo.debug[30].format(sys.exc_info()[-1].tb_lineno),e], 3)
        notify.counter += 1

    try:
        with open(config_getjudo.TEMP_FILE,"wb") as temp_file:
            pickle.dump(mydata, temp_file)
    except Exception as e:
        notify.publish([messages_getjudo.debug[29].format(sys.exc_info()[-1].tb_lineno),e], 3)
        notify.counter += 1

    if notify.counter >= config_getjudo.MAX_RETRIES:
        notify.publish(messages_getjudo.debug[32].format(config_getjudo.MAX_RETRIES),1)
        sys.exit()
    else:
        notify.counter = 0
#---------------------

Function_Caller(config_getjudo.STATE_UPDATE_INTERVAL, main).start()

notify.publish(messages_getjudo.debug[39], 2)   #Init Complete

