#!/usr/bin/python3
# -*- coding: utf-8 -*-

import config_getjudo

#DE
if config_getjudo.LANGUAGE == "DE":

    holiday_options = ["Aus", "Absperren", "Urlaubsmodus_1", "Urlaubsmodus_2"]

    entities = {
        0 : "Revision_in",
        1 : "Gesamtwasserverbrauch",
        2 : "Gesamtweichwasseranteil",
        3 : "Gesamthartwasseranteil",
        4 : "Salzvorrat",
        5 : "Salzreichweite",
        6 : "Wunschwasserhaerte",
        7 : "Rohwasserhaerte",
        8 : "Wasserdurchflussmenge",
        9 : "Batterierestkapazitaet",
        10 : "Anzahl_Regenerationen",
        11 : "Wasser_absperren",
        12 : "Regeneration",
        13 : "Sleepmode",
        14 : "Verbrauch_Heute",
        15 : "Verbrauch_Gestern",
        16 : "Meldung",
        17 : "max_Entnahmedauer",
        18 : "max_Wasserdurchfluss",
        19 : "max_Entnahmemenge",
        20 : "Urlaubsmodus"
    }

    debug = {
        1: "Verbunden mit MQTT Broker...",
        2: "Topics wurden abonniert...",
        3: "Autoconfigs wurden gesendet...",
        4: "Verbindung fehlgeschlagen, Fehlercode {}", #{rc}
        5: "Eingehende Nachricht: {}{}", #{message.topic},{message.payload}
        6: "Falscher Befehl!!",
        7: "Leckageschutz wurde erfolgreich auf \"{}\" gestellt ", #{pos}
        8: "HTTP-Fehler beim Schalten des Leckageschutzes",
        9: "Befehlsfehler!!",
        10: "Sleepmode wurde erfolgreich deaktiviert. Der Leckageschutz ist wieder aktiv",
        11: "HTTP-Fehler beim Deaktivieren des Sleepmodes",
        12: "Sleepmode-Zeit wurde erfolgreich auf {}h eingestellt", #{hours}
        13: "HTTP-Fehler beim Einstellen der Sleepmode-Zeit",
        14: "Sleepmode wurde erfolgreich eingeschaltet. Der Leckageschutz ist vorrübergehend deaktiviert",
        15: "HTTP-Fehler beim Aktivieren des Sleepmodes",
        16: "Regeneration wurde erfolgreich gestartet",
        17: "HTTP-Fehler beim Starten der Regeneration",
        18: "{} wurde erfolgreich auf den Wert {} gesetzt", #{obj.name}, {value}
        19: "HTTP-Fehler beim setzen des Werts von: {}", #{obj.name}
        20: "Fehler bei der int nach hex Umrechnung",
        21: "myjudo.eu-login fehlgeschlagen! - Falsche Zugangsdaten??",
        22: "Login erfolgreich, neuer Token: {} !!!!Achtung, Diesen Token nirgendwo Posten oder Verschicken. Hierdurch erhält man Vollzugriff auf die Anlage!!!!", #{login_response_json['token']}
        23: "Kein valider Token, versuche einen Neuen zu bekommen...",
        24: "Fehlerhafte Antwort vom Server: {}", #{val}
        25: "Falsche, unspezifische Antwort vom Server ",
        26: "Fehler bei MQTT Autoconfig",
        27: "Scriptfehler - Befehl senden fehlgeschlagen in Zeile: {}", 
        28: "Scriptfehler - Judo-login fehlgeschlagen in Zeile: {}",
        29: "Scriptfehler - Laden der Variablen aus Datei fehlgeschlagen in Zeile: {}",
        30: "Scriptfehler - Fehler beim Auswerten des Fehlerspeichers in Zeile: {}",
        31: "Scriptfehler - Fehler beim Holen und Auswerten der Gerätedaten in Zeile: {}",
        32: "{} Fehler in Folge beim Auswerten oder Erhalten der Daten. Gebe auf!! -> Fehlerhafte Internetverbindung???", #{config_getjudo.MAX_RETRIES}
        33: "MQTT Login fehlgeschlagen, beende Script!",
        34: "Lade gespeicherte Variablen",
        35: "Letzte Fehler-ID: {}",
        36: "Wasserverbrauch gestern: {}",
        37: "Offset für heutigen Wasserverbrauch: {}",
        38: "Letzte Ausführung des Scripts: {}",
        39: "Initialisierung erfolgreich!",
        40: "Urlaubsmodus wurde erfolgreich deaktiviert",
        41: "Tempfile scheinbar korrupt oder nicht vorhanden, Schreibe neu",
        42: "Beende Script. Schwerwiegender Fehler in Zeile: {}"

    }

    warnings = {
        "20": "Leckageschutz geschlossen.",
        "21": "Leckageschutz geschlossen Max. Entnahmemenge überschritten. Prüfen, ob Leckage vorliegt.",
        "22": "Leckageschutz geschlossen Max. Entnahmedauer überschritten. Prüfen, ob Leckage vorliegt.",
        "23": "Leckageschutz geschlossen Max. Volumenstrom überschritten. Prüfen, ob Leckage vorliegt.",
        "24": "Leckagesensor meldet Leckage. Prüfen, ob Leckage vorliegt.",
        "251": "Leckageschutz im Urlaubsmodus. Grenzwerte für die Wasserentnahme sind reduziert.",
        "253": "Leckageschutz im Urlaubsmodus. Leckageschutz geschlossen.",
        "26": "Leckageschutz im Sleepmodus, Restdauer $$$ Stunden.",
        "27": "Wartung/Service.",
        "28": "Salzvorrat prüfen.",
        "29": "Achtung Salzmangel",
        "30": "Regeneration läuft.",
        "31": "Batterie Kapazität $$$ %",
        "32": "Batterie leer!",
        "40": "Störung! Regenerationsantrieb defekt. Bitte verständigen Sie den Kundendienst.",
        "41": "Störung! Solestand im Salzbehälter zu hoch. Bitte verständigen Sie den Kundendienst.",
        "42": "Störung! Fehlfunktion Füllventil. Bitte verständigen Sie den Kundendienst.",
        "43": "Störung! Leckageschutz defekt. Bitte verständigen Sie den Kundendienst.",
        "46": "Leckageschutz im Sonderregelungsmodus.",
        "51": "Leckageschutz Max. Entnahmemenge überschritten. Prüfen, ob Leckage vorliegt.",
        "52": "Leckageschutz Max. Entnahmedauer überschritten. Prüfen, ob Leckage vorliegt.",
        "53": "Leckageschutz Max. Volumenstrom überschritten. Prüfen, ob Leckage vorliegt.",
        "151": "Leckagealarm Max. Entnahmemenge überschritten. Prüfen, ob Leckage vorliegt.",
        "152": "Leckagealarm Max. Entnahmedauer überschritten. Prüfen, ob Leckage vorliegt.",
        "153": "Leckagealarm Max. Volumenstrom überschritten. Prüfen, ob Leckage vorliegt.",
        "61": "Füllventil geschlossen. Maximale Füllzeit überschritten. Prüfen, ob Leckage vorliegt.",
        "62": "Füllventil geschlossen. Maximale Füllmenge überschritten. Prüfen, ob Leckage vorliegt.",
        "63": "Füllventil geschlossen. Maximale Füllzyklen überschritten. Prüfen, ob Leckage vorliegt.",
        "64": "Patrone verbraucht. Einbau einer neuen Patrone erforderlich.",
        "65": "Störung! Drucksensor defekt. Bitte verständigen Sie den Kundendienst.",
        "66": "Störung! Grundstellung. Bitte verständigen Sie den Kundendienst.",
        "67": "Störung! Tastatur defekt. Bitte verständigen Sie den Kundendienst.",
        "68": "Störung! Ventil undicht. Bitte verständigen Sie den Kundendienst.",
        "69": "Leckageschutz im Sleepmodus, Restdauer $$$ Stunden.",
        "70": "Leckageschutz geschlossen, Bodensensor meldet Leckage. Prüfen, ob Leckage vorliegt.",
        "71": "Im Lernmodus, Leckageschutz geschlossen, max. Entnahmemenge wurde überschritten. Prüfen ob Leckage vorliegt.",
        "72": "Im Lernmodus, Leckageschutz geschlossen, max. Volumenstrom wurde überschritten. Prüfen ob Leckage vorliegt.",
        "73": "Im Lernmodus, Leckageschutz geschlossen, max. Entnahmedauer wurde überschritten. Prüfen ob Leckage vorliegt.",
        "74": "Störung! Kugelventil defekt. Bitte verständigen Sie den Kundendienst."
    }

    errors = {
        "1": "Regenerationsantrieb defekt",
        "2": "Solestand im Salzbehälter hoch",
        "3": "Fehlfunktion beim Nachfüllen",
        "4": "Wasserstoppantrieb defekt",
        "5": "VSV defekt",
        "6": "Leitwertmessung defekt",
        "7": "Temperaturmessung defekt",
        "8": "Weichwasserzähler defekt",
        "9": "Rohwasserzähler defekt",
        "10": "RH < 2x MH",
        "11": "Lsu oder Lgnd wird nicht erkannt",
        "12": "Lso immer nass",
        "13": "Doppelfehler: Lsu wird nicht erkannt und Lso dauernd nass",
        "14": "RS 485 Verbindungs-problem"
    }

#ENG
else:

    holiday_options = ["Off", "Waterlock", "Holidaymode_1", "Holidaymode_2"]

    entities = {
        0: "Revision_in",
        1: "Total_water_consumption",
        2: "Total_softwater_proportion",
        3: "Total_hardwater_proportion",
        4: "Salt_stock",
        5: "Salt_range",
        6: "Output_hardness",
        7: "Input_hardness",
        8: "Water_flow_rate",
        9: "Battery_capacity",
        10: "Regeneration_count",
        11: "Water_lock",
        12: "Regeneration",
        13: "Sleepmode",
        14: "Consumption_today",
        15: "Consumption_yesterday",
        16: "Notification",
        17: "max_withdrawal_quantity",
        18: "max_volumetric_flow_rate",
        19: "max_consumption",
        20: "Holiday_mode"
    }

    debug = {
        1: "Connected to MQTT Broker...",
        2: "Topics has been subscribed...",
        3: "Autoconfigs has been sent...",
        4: "Failed to connect, return code {}",
        5: "Incomming Message: {}{}",
        6: "Command_Name_Error!!",
        7: "Leackage protection has been switched {} successfully ",
        8: "HTTP Error while setting the leackage protection",
        9: "Command_Error!!",
        10: "Sleepmode has been successfully disabled, Leakage protection is active now",
        11: "HTTP Error while disabling the sleepmode",
        12: "Sleepmodetime was set to {}h successfully",
        13: "HTTP Error while setting up the sleepmode-time",
        14: "Sleepmode has been successfully enabled, Leakage protection is disabled now",
        15: "HTTP Error while enabling the sleepmode",
        16: "Regeneration has been started successfully",
        17: "HTTP Error while setting the regeneration-trigger",
        18: "{} has been set to {} successfully",
        19: "HTTP Error while setting {}",
        20: "failed by int to hex conversion",
        21: "myjudo.eu login failed! - Wrong credentials?? EXIT",
        22: "Login successful, got new token: {}", #{login_response_json['token']} !!!!Attention, Don't Post or Publish this Token anywhere. It allows grand access to the plant!!!!",
        23: "Error: No valid Token, trying to get a new one...",
        24: "Response Error: {}",
        25: "Error: Unspecific response status",
        26: "Error while MQTT autoconfig",
        27: "Script error - failed to send command on line: {}", 
        28: "Script error - failed judo login on line: {}",
        29: "Script error - loading variables failed on line: {}",
        30: "Script error - getting or parsing fault memory failed on line: {}",
        31: "Script error - getting or parsing data failed on line: {}",
        32: "{} errors while fetching data in sequence. Giving up!! -> Faulty internet connection???", #{config_getjudo.MAX_RETRIES}
        33: "MQTT login failed, canceling the script",
        34: "Loading stored variables",
        35: "Last error-ID: {}",
        36: "Total water consumption yesterday: {}",
        37: "Offset for todays waterconsumption: {}",
        38: "Last run of script: {}",
        39: "Init successful!",
        40: "Holidaymode has been deactivated successfully",
        41: "Temp-file seems to be currupt or not existent, writing a new one",
        42: "Canceling Script, Fatal Error on line: {}"
    }


    warnings = {
        "20": "Leakage protection closed.",
        "21": "Leakage protection closed Max. water quantity exceeded. Check if there is a leakage.",
        "22": "Leakage protection closed Max. sampling duration exceeded. Check if there is a leakage.",
        "23": "Leakage protection closed Max. water flow exceeded. Check if there is a leakage.",
        "24": "Leak sensor reports a leakage. Check if there is a leakage.",
        "251": "Leakage protection in holiday mode. Limit values for water sampling are reduced.",
        "253": "Leakage protection in holiday mode. Leakage protection closed.",
        "26": "Leakage protection in sleep mode, remaining duration $$$ hours.",
        "27": "Maintenance/service.",
        "28": "Check salt storage.",
        "29": "Attention lack of salt",
        "30": "Regeneration is running",
        "31": "Battery capacity $$$ %",
        "32": "Battery empty!",
        "40": "Fault! Regeneration drive defective. Kindly contact the customer service.",
        "41": "Fault! Brine level in salt container too high. Kindly contact the customer service.",
        "42": "Fault! Malfunction filling valve Kindly contact the customer service.",
        "43": "Fault! Leakage protection defective. Kindly contact the customer service.",
        "46": "Leckageschutz im Sonderregelungsmodus.",
        "51": "Leakage protection closed Max. water quantity exceeded. Check if there is a leakage.",
        "52": "Leakage protection closed Max. sampling duration exceeded. Check if there is a leakage.",
        "53": "Leakage protection closed Max. water flow exceeded. Check if there is a leakage.",
        "151": "Leakage protection closed Max. water quantity exceeded. Check if there is a leakage.",
        "152": "Leakage protection closed Max. sampling duration exceeded. Check if there is a leakage.",
        "153": "Leakage protection closed Max. water flow exceeded. Check if there is a leakage.",
        "61": "Filling valve is closed. Max. filling duration is exceeded. Check if there is a leakage.",
        "62": "Filling valve is closed. Max. filling quantity is exceeded. Check if there is a leakage.",
        "63": "Filling valve is closed. Max. number of filling cycles is exceeded. Check if there is a leakage.",
        "64": "Filling cartridge is empty. Installation of new filling cartridge necessary.",
        "65": "Fault! Pressure sensor defectiv. Kindly contact the customer service.",
        "66": "Fault! Basic position. Kindly contact the customer service.",
        "67": "Fault! Keyboard defectiv. Kindly contact the customer service.",
        "68": "Fault! Filling valve  leaky. Kindly contact the customer service.",
        "69": "Leakage protection in sleep mode, remaining duration $$$ hours.",
        "70": "Leakage protection closed, bottom sensor reports leakage. Check if there is a leakage.",
        "71": "Teachingmode, Leakage protection closed Max. water quantity exceeded. Check if there is a leakage.",
        "72": "Teachingmode, Leakage protection closed Max. sampling duration exceeded. Check if there is a leakage.",
        "73": "Teachingmode, Leakage protection closed Max. water flow exceeded. Check if there is a leakage.",
        "74": "Fault! Ball valve defect. Kindly contact the customer service."
    }

    errors = {
        "1": "Regeneration drive defective",
        "2": "Brine level in salt container high",
        "3": "Malfunction during refilling",
        "4": "Water stop drive defective",
        "5": "VSV defective",
        "6": "Conductivity measurement defective",
        "7": "Temperature measurement defective",
        "8": "Soft water counter defective",
        "9": "Raw water counter defective",
        "10": "RH < 2x MH",
        "11": "Lsu or Lgnd is not detected",
        "12": "Lso always wet",
        "13": "Double fault: Lsu is not detected and Lso always wet",
        "14": "RS 485 connection problem"
    }






