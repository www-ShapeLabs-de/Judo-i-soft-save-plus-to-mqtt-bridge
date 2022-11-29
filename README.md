# Judo i-soft save+ to mqtt bridge for homeassistant
A small device to write and read settings to Judo i-soft safe+ water softening system with homeassistant.


This is a small workarount to read and control the Judo isoft safe+ water softener with homeassisant (hassio). It is the version with the small character-lcd and leakage protection.

Unfortunately it is not possible to communicate directly with this version of the plant. Port 8000 and port 8124, through which the system can be read out on the Judo isoft-plus, are closed. The only way to access settings and data is via the cloud server.

Notice:
There are 2 versions of the system, which sound very similar.
- i-soft safe+ (small display, leakage protection) --->This repo
- i-soft plus (large graphic display) ---> another tutorials, like this: https://blog.muwave.de/2017/06/monitoring-and-controlling-a-judo-i-soft-plus-water-softening-device-via-lan/

To do this, you must register the system for the cloud service as described in the user manual and create a user account. There is also a judo smartphone app for this, but it is of course nicer to have everything in homeassisant :-)

The hardware of this project consists of an ESP8266 in basic circuitry. You can also just use a node MCU etc.. No further components are necessary.

In the software you have to configure the #define-macros (wifi, mqtt-server, location, name etc).

It is necessary to generate a token. To do this, log into the cloud service with your user account on https://www.myjudo.eu.

After the successful login, you can copy the hexadecimal-token (just take the "knmtoken" not the "judotoken") from the URL in the address bar of the browser.

The token must then be inserted under #define TOKEN in the code.

The token can be used to create a URL that can also be used to read out the serial number and all other data:

https://www.myjudo.eu/interface/?token=INSERT_TOKEN_HERE&group=register&command=get%20device%20data

As a response you get the complete data set, which also contains the serial number of the device at the beginning, which must then be entered in the code under #define SERIALNUMBER.

With this the configuration is finished. The software can be flashed into the ESP. Afterwards the device should set itself up automatically with mqtt-autoconfig in homeassitant with all entities:

- reading (sensors): 
  - total water consumption
  - total softwater consumption
  - salt stock
  - salt range
  - output hardness
  - input hardness
  - water flow
  - capacity of battery
  - number of regenerations
- writing:
  - leakage protection (switch)
  - output hardness (input number slider)



This Project based of informations from:
- https://blog.muwave.de/2017/06/monitoring-and-controlling-a-judo-i-soft-plus-water-softening-device-via-lan/
- https://forum.fhem.de/index.php/topic,115696.15.html
- https://knx-user-forum.de/forum/projektforen/edomi/1453632-lbs19002090-judo-i-soft-wasserenth%C3%A4rtungsanlage/page2
- https://github.com/arteck/iobroker.judoisoft/blob/master/lib/dataConverter.js

Many thanks to this guys!!!

