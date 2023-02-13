import time
import sys
import appdaemon.plugins.hass.hassapi as hass
import config_getjudo

class main_loop(hass.Hass):
    def initialize(self):
        import getjudo


