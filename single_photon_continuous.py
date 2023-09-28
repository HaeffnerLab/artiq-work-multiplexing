from artiq.experiment import *
class ContinuousDDS(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("urukul1_ch0")
        self.setattr_device("urukul1_ch1")
        self.setattr_argument(
            'att_397', NumberValue(ndecimals=2, step=1, default=2.8))
        self.setattr_argument(
            'att_866', NumberValue(ndecimals=2, step=1, default=8.43))
        self.setattr_argument(
            'freq_397', NumberValue(ndecimals=2, step=1, default=200.0))
        self.setattr_argument(
            'freq_866', NumberValue(ndecimals=2, step=1, default=85.0))
    @kernel
    def run(self):
        self.core.reset()
        self.urukul1_ch0.init()
        self.urukul1_ch1.init()
        self.urukul1_ch0.set_att(self.att_397*dB)
        self.urukul1_ch1.set_att(self.att_866*dB)
        self.urukul1_ch0.sw.on()
        self.urukul1_ch1.sw.on()
            # Max amplitde = 1.0
            #for i in range(1, 20):
        while True:
            self.urukul1_ch0.set(self.freq_397*MHz, amplitude=1.0)
            self.urukul1_ch1.set(self.freq_866*MHz, amplitude=1.0)
            delay(1*s)
        # self.urukul1_ch3.sw.off()
