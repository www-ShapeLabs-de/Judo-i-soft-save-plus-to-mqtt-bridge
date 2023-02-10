import time
import sys
import appdaemon.plugins.hass.hassapi as hass
import config_getjudo

class main_loop(hass.Hass):
    def initialize(self):
        if config_getjudo.APPDAEMON:
            import getjudo
        while True:
            #print("loop started")
            try: 
                if config_getjudo.APPDAEMON:
                    self.run_in(getjudo.main, config_getjudo.STATE_UPDATE_INTERVAL)
            except Exception as e:
                    crash = ["Error on line {}".format(sys.exc_info()[-1].tb_lineno),"\n",e]
                    print(crash)  
            #print("loop running")
            time.sleep(config_getjudo.STATE_UPDATE_INTERVAL) # TODO: find alternative to time.sleep!!!!
