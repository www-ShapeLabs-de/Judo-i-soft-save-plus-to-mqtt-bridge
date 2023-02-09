import time
import sys
import appdaemon.plugins.hass.hassapi as hass
import config_getjudo
#import config_getbayrol

class main_loop(hass.Hass):
    def initialize(self):
        if config_getjudo.APPDAEMON:
            import getjudo
        #if config_getbayrol.appdaemon:
        #    import getbayrol
        while True:
            #print("loop started")
            try: 
                if config_getjudo.APPDAEMON:
                    self.run_in(getjudo.main, config_getjudo.STATE_UPDATE_INTERVAL)
                #if config_getbayrol.appdaemon:
                #    self.run_in(getbayrol.loop, config_getbayrol.STATE_UPDATE_INTERVAL)
            except Exception as e:
                    crash = ["Error on line {}".format(sys.exc_info()[-1].tb_lineno),"\n",e]
                    print(crash)  
            #print("loop running")
            time.sleep(config_getjudo.STATE_UPDATE_INTERVAL)
