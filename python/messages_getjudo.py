#!/urs/bin/python3
# -*- coding: utf-8 -*-
import config_getjudo

#DE
if config_getjudo.MESSAGE_LANGUAGE == "DE":
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


else:
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
        "70": "Leckageschutz geschlossen, Bodensensor meldet Leckage. Prüfen, ob Leckage vorliegt.",
        "71": "Im Lernmodus, Leckageschutz geschlossen, max. Entnahmemenge wurde überschritten. Prüfen ob Leckage vorliegt.",
        "72": "Im Lernmodus, Leckageschutz geschlossen, max. Volumenstrom wurde überschritten. Prüfen ob Leckage vorliegt.",
        "73": "Im Lernmodus, Leckageschutz geschlossen, max. Entnahmedauer wurde überschritten. Prüfen ob Leckage vorliegt.",
        "74": "Störung! Kugelventil defekt. Bitte verständigen Sie den Kundendienst."
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


