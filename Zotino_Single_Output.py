from artiq.experiment import *                  #imports everything from artiq experiment library
#This code outputs a single voltage on a single Zotino channel
class Zotino_Single_Output(EnvExperiment):
    """DAC: Single Output"""
    def build(self): #this code runs on the host device
        self.setattr_device("core")             #adds drivers for core device as attributes
        self.setattr_device("zotino0")          #adds drivers for zotino board as attributes
        self.setattr_device('ttl8')         # Initialize channel 8 (Trigger)
    def prepare(self):
        self.trigger_ttl = self.ttl8
    @kernel                                                      # noqa F405
    def run_trigger(self, n=1, unit=us,                         # noqa F405
                    is_off_after_duration=True):
        self.core.break_realtime()
        with sequential:                                         # noqa F405
            self.trigger_ttl.on()
            self.trigger_ttl.output()
            self.trigger_ttl.pulse(n*unit)
            if is_off_after_duration:
                self.trigger_ttl.off()
    @kernel #this code runs on the FPGA
    def run(self):
        self.core.reset()                       #resets core device
        self.core.break_realtime()              #moves timestamp forward to prevent underflow
                                                #this can also be achieved with a fixed delay
        voltage = 1.585                             #defines voltage variable in Volts
        self.zotino0.init()                     #initialises zotino0
        delay(200*us)                           #200us delay, needed to prevent underflow on initialisation
        self.zotino0.write_dac(0,voltage)       #writes voltage variable to DAC, channel 0
        self.zotino0.load()                     #outputs previously loaded voltage
        self.run_trigger(n=1, unit=us)
