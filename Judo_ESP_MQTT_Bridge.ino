/*---------------------------------------------------------------------------
 Copyright:      Henning Schaper  mailto: henningschaper@gmx.de
 Author:         Henning Schaper
 Remarks:        none
 known Problems: none
 Version:        v1.0   25.11.2022
 Description:  	 Judo i-soft SAFE+ to MQTT Bridge for hassio
 				 Processor: ESP8266 (ESP12F)
 				 Features:  - homeassistant mqtt autoconfig
 				 			- OTA
 				 			- JSON over MQTT 
 				 			- https REST request from Cloud server (nessecary workarount, it's not possible to communicate directly with the i-soft SAFE+)
 				 			- static wifi, no wifimanager (more stable)

 Based on information from: (with many thanks)
 - https://forum.fhem.de/index.php/topic,115696.15.html
 - https://knx-user-forum.de/forum/projektforen/edomi/1453632-lbs19002090-judo-i-soft-wasserenth%C3%A4rtungsanlage/page2
 - https://github.com/arteck/iobroker.judoisoft/blob/master/lib/dataConverter.js
----------------------------------------------------------------------------*/

//----------------------- Includes  ----------------------//
//#include <ESP8266WiFi.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include <ArduinoOTA.h>
#include <ESP8266HTTPClient.h>

//------------------------ Config  -----------------------//
#define SOFTWARE_VERSION		"v1.0"
#define WLAN_SSID       		"my_wifi_ssid"
#define WLAN_PASS       		"my_wifi_pass"
#define MQTT_SERVER     		"192.168.2.5"
#define MQTT_SERVERPORT 		1883                   // use 8883 for SSL
#define MQTT_USERNAME   		"mqttuser"
#define MQTT_KEY        		"mqtt_pass"
#define LOCATION				"my_location"
#define NAME 					"Judo_isoftplus_bridge"
//#define OTA_PASS				"admin"
#define STATE_UPDATE_INTERVAL	20000 					//[ms]
#define AVAILABILITY_ONLINE "online"
#define AVAILABILITY_OFFLINE "offline"

#define TOKEN "1a2b3c4d5e6f1a2b3c4d5e6f1a2b3c4d"
#define SERIALNUMBER "123456789123"

#define DEBUG

//------------------- Constants & LUTs  -----------------//

//---------------------- Variables  ---------------------//
char identifier[24];

char MQTT_TOPIC_AVAILABILITY[128];
char MQTT_TOPIC_STATE[128];
char MQTT_TOPIC_COMMAND[128];
char device_info[127];

long total_water_consumption = 0;
long total_softwater_consumption = 0;
int salt_stock = 0;
int salt_range = 0;

int input_hardness = 0;
int output_hardness = 0; 
int water_flow = 0;
int regenerations = 0;
int batt_capacity = 0;
int water_lock= 0;

String https_json_response;
DynamicJsonDocument response(4096);

unsigned long stateUpdatePreviousMillis = millis();

//----------------------- Objects  ----------------------//
HTTPClient sender;
WiFiClientSecure net;
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

//-------------------- Main Programm  -------------------//
void setup() 
{
	Serial.begin(19200);
	Serial.println("Start INIT");

	delay(500);

	strcpy (device_info,"https://www.myjudo.eu/interface/?token=");
	strcat (device_info,TOKEN);
	strcat (device_info, "&group=register&command=get%20device%20data");

	snprintf(identifier, sizeof(identifier), "%s-%s",NAME,LOCATION);
	snprintf(MQTT_TOPIC_AVAILABILITY, 127, "%s/%s/status", LOCATION, NAME);
	snprintf(MQTT_TOPIC_STATE, 127, "%s/%s/state", LOCATION, NAME);
	snprintf(MQTT_TOPIC_COMMAND, 127, "%s/%s/command", LOCATION, NAME);

	connect_WiFi();
	setupOTA();

	mqttClient.setServer(MQTT_SERVER, MQTT_SERVERPORT);
	mqttClient.setKeepAlive(10);
	mqttClient.setBufferSize(2048);
	mqttClient.setCallback(mqttCallback);

	mqttReconnect();

	Serial.println("INIT COMPLETE!");
}

void loop() 
{
	mqttClient.loop();
	ArduinoOTA.handle();
	
	if(STATE_UPDATE_INTERVAL <= (millis() - stateUpdatePreviousMillis))
	{
		if (WiFi.status() != WL_CONNECTED) 
			connect_WiFi(); 

		if (!mqttClient.connected())
			mqttReconnect();

		publishState();
		stateUpdatePreviousMillis = millis();
	}
}

//---------------------- Fuctions  ----------------------//
void setupOTA()
{
	ArduinoOTA.onStart([]() { Serial.println("Start"); });
	ArduinoOTA.onEnd([]() { Serial.println("\nEnd"); });

	ArduinoOTA.onProgress([](unsigned int progress, unsigned int total)
	{
		Serial.printf("Progress: %u%%\r\n", (progress / (total / 100)));
	});

	ArduinoOTA.onError([](ota_error_t error)
	{
		Serial.printf("Error[%u]: ", error);
		if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
		else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
		else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
		else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
		else if (error == OTA_END_ERROR) Serial.println("End Failed");
	});

	ArduinoOTA.setHostname(identifier);
	#ifdef OTA_PASS
		ArduinoOTA.setPassword(OTA_PASS);
	#endif
	ArduinoOTA.begin();
}

void connect_WiFi()
{
	Serial.print("Connecting to ");
	Serial.println(WLAN_SSID);
	
	WiFi.mode(WIFI_STA);
	WiFi.begin(WLAN_SSID, WLAN_PASS);

	while (WiFi.status() != WL_CONNECTED)
	{
		delay(100);
		Serial.print(".");
	}

	Serial.println("");
	Serial.println("WiFi connected");
	Serial.println("IP address: ");
	Serial.println(WiFi.localIP());
	net.setInsecure();
}

void mqttReconnect()
{
	for(int attempt = 0; attempt < 3; ++attempt) 
	{
		Serial.print("Connecting MQTT....");
		if(mqttClient.connect(identifier, MQTT_USERNAME, MQTT_KEY, AVAILABILITY_ONLINE, 1, true, AVAILABILITY_OFFLINE)) 
		{	
			Serial.println("Connected!");
			mqttClient.publish(MQTT_TOPIC_AVAILABILITY, AVAILABILITY_ONLINE, true);
			
			Serial.println("Sending Autoconfig....");

			publish_autoconfig_entity("WiFi","dBm","mdi:wifi",3);
			publish_autoconfig_entity("Gesamtwasserverbrauch","L","mdi:water",3);
			publish_autoconfig_entity("Gesamtweichwasserverbrauch","L","mdi:water-outline",3);
			publish_autoconfig_entity("Salzvorrat","g","mdi:gradient-vertical",3);
			publish_autoconfig_entity("Salzreichweite","Tage","mdi:chevron-triple-right",3);
			publish_autoconfig_entity("Wunschwasserhaerte","°dH","mdi:water-minus",1);
			publish_autoconfig_entity("Restwasserhaerte","°dH","mdi:water-minus",3);
			publish_autoconfig_entity("Rohwasserhaerte","°dH","mdi:water-plus",3);
			publish_autoconfig_entity("Wasserdurchflussmenge","L/min","mdi:waves-arrow-right",3);
			publish_autoconfig_entity("Batterierestkapazität","%","mdi:battery-50",3);
			publish_autoconfig_entity("Regenerationen"," ","mdi:recycle-variant",3);
			publish_autoconfig_entity("ESP_Reset"," ","mdi:replay" ,2);
			publish_autoconfig_entity("Wasser_Absperren"," ","mdi:pipe-valve" ,2);
			Serial.println("Subscribing Topics....");
			mqttClient.subscribe(MQTT_TOPIC_COMMAND);
			Serial.println("Success!");
			break;
		}
		else
		{
			delay(5000);
			Serial.print("FAILED, Retry...");
		}
	}
}

void publishState()
{
	DynamicJsonDocument stateJson(512);
	char payload[512];

	if(getRequest(device_info))
		parse_data();
	#ifdef DEBUG
		Serial.print("Wasserverbrauch total: ");
		Serial.print(total_water_consumption);
		Serial.println(" Liter");
		Serial.print("Weichwasserverbrauch total: ");
		Serial.print(total_softwater_consumption);
		Serial.println(" Liter");
		Serial.print("Salzvorrat: ");
		Serial.print(salt_stock);
		Serial.println(" g");
		Serial.print("Salz-Reichweite: ");
		Serial.print(salt_range);
		Serial.println(" Tage");
		Serial.print("Restwasserhaerte: ");
		Serial.print(output_hardness);
		Serial.println(" dH");
		Serial.print("Rohwasserhaerte: ");
		Serial.print(input_hardness);
		Serial.println(" dH");
		Serial.print("Wasserdurchflussmenge: ");
		Serial.print(water_flow);
		Serial.println(" Lpm");
		Serial.print("Batterierestkapazitaet: ");
		Serial.print(batt_capacity);
		Serial.println(" Prozent");
		Serial.print("Anzahl Regenerationen: ");
		Serial.println(regenerations);
		Serial.print("Wasser Abgesperrt: ");
		Serial.println(water_lock)
		Serial.println(" ");
		Serial.println(" ");
	#endif
		
	stateJson["ESP_Reset"] = "off";
	stateJson["WiFi"] = WiFi.RSSI();
	stateJson["Gesamtwasserverbrauch"] = String(total_water_consumption);
	stateJson["Gesamtweichwasserverbrauch"] = String(total_softwater_consumption);
	stateJson["Salzvorrat"] = String(salt_stock);
	stateJson["Salzreichweite"] = String(salt_range);
	stateJson["Restwasserhaerte"] = String(output_hardness);
	stateJson["Wunschwasserhaerte"] = String(output_hardness);
	stateJson["Rohwasserhaerte"] = String(input_hardness);
	stateJson["Wasserdurchflussmenge"] = String(water_flow);
	stateJson["Batterierestkapazitaet"] = String(batt_capacity);
	stateJson["Regenerationen"] = String(regenerations);

	if (water_lock)
		stateJson["Wasser_Absperren"] = "on";
	else
		stateJson["Wasser_Absperren"] = "off";

	serializeJson(stateJson, payload);
	mqttClient.publish(MQTT_TOPIC_STATE, payload, true);

	stateUpdatePreviousMillis = millis();
}

void mqttCallback (char* topic, byte* payload, unsigned int length)
{
	if (strcmp(topic, MQTT_TOPIC_COMMAND) == 0)
	{
		DynamicJsonDocument commandJson(256);
		char payloadText[length + 1];
		snprintf(payloadText, length + 1, "%s", payload);
		DeserializationError err = deserializeJson(commandJson, payloadText);

		if (!err)
		{
			String reset = commandJson["ESP_Reset"].as<String>();
			if (reset == "on")
				Reset_ESP();									//ECHO
			String water_lock_sw = commandJson["Wasser_Absperren"].as<String>();

			if (water_lock_sw == "on")
				switch_valve(1);
				
			else if (water_lock_sw == "off")
				switch_valve(0);
			else
			{
				String output_hardness_sw = commandJson["Wunschwasserhaerte"].as<String>();
				set_water_hardness(output_hardness_sw.toInt());
			}
		}
	}
}

//TYPE: 1=Input-Number, 2=Switch, 3=Sensor
void publish_autoconfig_entity(const char value_name[], const char unit[], const char icon[], uint8_t type)
{
	char mqttPayload[1024];
	DynamicJsonDocument autoconfPayload(1024);
	DynamicJsonDocument device(256);
	char MQTT_TOPIC_AUTOCONF_TOPIC[128];

	device["identifiers"] = String("[") + identifier + String("]");
	device["manufacturer"] = "ShapeLabs.de";
	device["model"] = NAME;
	device["name"] = identifier;
	device["sw_version"] = SOFTWARE_VERSION;
	autoconfPayload["device"] = device.as<JsonObject>();
	autoconfPayload["availability_topic"] = MQTT_TOPIC_AVAILABILITY;
	autoconfPayload["state_topic"] = MQTT_TOPIC_STATE;
	autoconfPayload["name"] = identifier + String(" ") + value_name;
	autoconfPayload["unique_id"] = identifier + String("_") + value_name;
	autoconfPayload["icon"] = icon;
	autoconfPayload["value_template"] = String("{{value_json.") + value_name + String("}}");
	
	if(type==1)
	{
		autoconfPayload["command_topic"] = MQTT_TOPIC_COMMAND;
		autoconfPayload["unit_of_measurement"] = unit;
		autoconfPayload["min"] = "1";
		autoconfPayload["max"] = "15";
		autoconfPayload["command_template"] = String("{\"") + value_name + String("\": {{ value }}}");

		snprintf(MQTT_TOPIC_AUTOCONF_TOPIC, 127, "homeassistant/number/%s/%s_%s/config", LOCATION, NAME, value_name);
	}
	else if(type==2)
	{
		autoconfPayload["command_topic"] = MQTT_TOPIC_COMMAND;
		autoconfPayload["payload_on"] = String("{\"") + value_name + String("\": \"on\"}");
		autoconfPayload["payload_off"] = String("{\"") + value_name + String("\": \"off\"}");
		autoconfPayload["state_on"] = "on";
		autoconfPayload["state_off"] = "off";
		snprintf(MQTT_TOPIC_AUTOCONF_TOPIC, 127, "homeassistant/switch/%s/%s_%s/config", LOCATION, NAME, value_name);
	}
	if(type == 3)
	{
		autoconfPayload["unit_of_measurement"] = unit;
		snprintf(MQTT_TOPIC_AUTOCONF_TOPIC, 127, "homeassistant/sensor/%s/%s_%s/config", LOCATION, NAME, value_name);
	}

	serializeJson(autoconfPayload, mqttPayload);
	mqttClient.publish(MQTT_TOPIC_AUTOCONF_TOPIC, mqttPayload, true);
	device.clear();
	autoconfPayload.clear();
	delay(100);
}

bool getRequest(const char* command)
{
	if(sender.begin(net, command)) 
	{
		int httpCode = sender.GET(); 
		
		if (httpCode) 
 		{
			if (httpCode == 200) 
			{
				DeserializationError error = deserializeJson(response,sender.getString());

				if(error) 
				{
					Serial.print(F("Deserialize failed!"));
					return 0;
				}
			}
 			else
 			{
				Serial.print("HTTP-Error: " +  String(httpCode));
				return 0;
 			}
		}
		sender.end();
		return 1;
	}
	else
	{
		Serial.printf("HTTP-Verbindung konnte nicht hergestellt werden!");
		return 0;
	}
}

void parse_data()
{
	String val;
	String sub_a; 
	String sub_b; 
	String sub_c; 
	String sub_d; 


	val = response["data"][0]["data"][0]["data"]["8"]["data"].as<String>();;
	sub_a = val.substring(0,2);
	sub_b = val.substring(2,4);
	sub_c = val.substring(4,6);
	sub_d = val.substring(6,8);
	val = sub_d + sub_c + sub_b + sub_a;

	total_water_consumption = strtol(val.c_str(), NULL, 16);

	val = response["data"][0]["data"][0]["data"]["9"]["data"].as<String>();;

	sub_a = val.substring(0,2);
	sub_b = val.substring(2,4);
	sub_c = val.substring(4,6);
	sub_d = val.substring(6,8);
	val = sub_d + sub_c + sub_b + sub_a;

	total_softwater_consumption = strtol(val.c_str(), NULL, 16);

	val = response["data"][0]["data"][0]["data"]["94"]["data"].as<String>();;
	sub_a = val.substring(0,2);
	sub_b = val.substring(2,4);
	val = sub_b + sub_a;
	salt_stock = strtol(val.c_str(), NULL, 16);

	val = response["data"][0]["data"][0]["data"]["94"]["data"].as<String>();;
	sub_a = val.substring(4,6);
	sub_b = val.substring(6,8);
	val = sub_b + sub_a;
	salt_range = strtol(val.c_str(), NULL, 16);


	val = response["data"][0]["data"][0]["data"]["790"]["data"].as<String>();;
	sub_a =val.substring(18,20);
	output_hardness = strtol(sub_a.c_str(), NULL, 16);

	sub_b = val.substring(54,56);
	input_hardness = strtol(sub_b.c_str(), NULL, 16);

	sub_c = val.substring(32,34);
	sub_d = val.substring(34,36);
	val = sub_d + sub_c;
	water_flow = strtol(val.c_str(), NULL, 16);



	val = response["data"][0]["data"][0]["data"]["791"]["data"].as<String>();;
	sub_a = val.substring(62,64);
	sub_b = val.substring(64,66);
	val = sub_b + sub_a;
	regenerations = strtol(val.c_str(), NULL, 16);


	val = response["data"][0]["data"][0]["data"]["93"]["data"].as<String>();;
	sub_a =val.substring(6,8);
	batt_capacity = strtol(sub_a.c_str(), NULL, 16);

	val = response["data"][0]["data"][0]["data"]["792"]["data"].as<String>();;
	sub_a =val.substring(2,4);
	water_lock = strtol(sub_a.c_str(), NULL, 16);
	if(water_lock)
		water_lock = 1;
}

void Reset_ESP()
{
	WiFi.disconnect(true);
	delay(1000);
	ESP.restart();	
}

bool switch_valve(uint8_t pos)							//pos 0=open, 1=close
{
	if(pos>1)
		pos = 1;

	char valve_action[255];

	strcpy (valve_action,"https://www.myjudo.eu/interface/?token=");
	strcat (valve_action,TOKEN);
	strcat (valve_action, "&group=register&command=write%20data&serial_number=");
	strcat (valve_action,SERIALNUMBER);

if(!pos && water_lock)//OPEN
	{
		strcat (valve_action, "&dt=0x33&index=73&data=&da=0x1&role=customer");
		if(getRequest(valve_action))
		{
			publishState();

			if(!water_lock)
			{
				Serial.println("-->Leckageschutz geöffnet");
				return 1;
			}
			else
			{
				Serial.println("-->ERROR!");
				return 0;
			}
		}
		else
		{
			Serial.println("-->HTTP ERROR!");
			return 0;
		}

	}
else if (pos && !water_lock)//CLOSE
	{
		strcat (valve_action, "&dt=0x33&index=72&data=&da=0x1&role=customer");
		if(getRequest(valve_action))
		{
			publishState();
			if(water_lock)
			{
				Serial.println("-->Leckageschutz geschlossen");
				return 1;
			}
			else
			{
				Serial.println("-->ERROR!");
				return 0;
			}
		}
		else
		{
			Serial.println("-->HTTP ERROR!");
			return 0;
		}
	}
	return 0;
}

void set_water_hardness(uint8_t val)
{
	if(val < 1) val = 1;
	else if(val > 15) val =15;

	char s[1];
	sprintf (s, "%1x", val);
	char hardness_action[255];
	strcpy (hardness_action,"https://www.myjudo.eu/interface/?token=");
	strcat (hardness_action,TOKEN);
	strcat (hardness_action, "&group=register&command=write%20data&serial_number=");
	strcat (hardness_action,SERIALNUMBER);
	strcat (hardness_action, "&dt=0x33&index=60&data=");
	strcat (hardness_action, s);
	strcat (hardness_action, "&da=0x1&role=customer&action=normal");

	if(getRequest(hardness_action))
	{
		publishState();

		Serial.print("-->Wunschwasserhaerte auf ");
		Serial.print(output_hardness);
		Serial.println("dh eingestellt");

	}
	else
		Serial.println("-->HTTP ERROR!");
}








