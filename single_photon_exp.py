from artiq.experiment import *                                   # noqa F403
class SinglePhoton(EnvExperiment):                               # noqa F405
    def build(self):
        self.setattr_device('core')
        self.setattr_device('urukul1_ch0')  # Initialize DDS 0 (397nm)
        self.setattr_device('urukul1_ch1')  # Initialize DDS 1 (397nm)
        self.setattr_device('ttl0')         # Initialize channel 0 (PMT1)
        self.setattr_device('ttl1')         # Initialize channel 1 (PMT2)
        self.setattr_device('ttl8')         # Initialize channel 8 (Trigger)
        self.setattr_argument(
            'att_397', NumberValue(ndecimals=2, step=1, default=2.8))
        self.setattr_argument(
            'att_866', NumberValue(ndecimals=2, step=1, default=8.43))
        self.setattr_argument(
            'freq_397', NumberValue(ndecimals=2, step=1, default=195))
        self.setattr_argument(
            'freq_866', NumberValue(ndecimals=2, step=1, default=75))
    def prepare(self):
        self.rep = 50
        self.ddses = [
            self.urukul1_ch0,
            self.urukul1_ch1,
        ]
        self.pmt_ttls = [
            self.ttl0,
            self.ttl1
        ]
        print(self.att_397, self.att_866)
        self.trigger_ttl = self.ttl8
    @kernel                                                      # noqa F405
    def run_doppler_cooling(self):
        self.core.break_realtime()
        with parallel:                                           # noqa F405
            with sequential:
                self.ddses[0].sw.on()
                self.ddses[1].sw.on()
                self.ddses[0].set(frequency=200*MHz, amplitude=1.0) # noqa F405
                self.ddses[1].set(frequency=85*MHz, amplitude=1.0) # noqa F405
                delay(0.5*ms)
                self.ddses[0].sw.off()
                self.ddses[1].sw.off()
    @kernel
    def run_397_photon_generation(self):
        self.core.break_realtime()
        with sequential:                                         # noqa F405
            self.ddses[0].sw.on()
            self.ddses[0].set(frequency=self.freq_397*MHz, amplitude=1.0) # noqa F405
            delay(5*us)                                          # noqa F405
            self.ddses[0].sw.off()
            delay(1*us)                                          # noqa F405
    @kernel
    def run_866_photon_generation(self):
        self.core.break_realtime()
        with sequential:                                         # noqa F405
            self.ddses[1].sw.on()
            self.ddses[1].set(frequency=self.freq_866*MHz, amplitude=1.0) # noqa F405
            delay(1*us)                                          # noqa F405
            self.ddses[1].sw.off()
            delay(0.5*us)                                        # noqa F405
    @kernel                                                      # noqa F405
    def run_pmts(self):
        self.core.break_realtime()
        tr_count = 0
        for ttl in self.pmt_ttls:
            ttl.input()
        count = 0
        for ttl in self.pmt_ttls:
            self.core.break_realtime()
            tr_count = ttl.gate_rising(1000*ns)                  # noqa F405
            count += 1
        # TODO
    @kernel                                                      # noqa F405
    def run_trigger(self, n=10, unit=us,                         # noqa F405
                    is_off_after_duration=True):
        self.core.break_realtime()
        with sequential:                                         # noqa F405
            self.trigger_ttl.on()
            self.trigger_ttl.output()
            self.trigger_ttl.pulse(n*unit)
            if is_off_after_duration:
                self.trigger_ttl.off()
    @kernel                                                      # noqa F405
    def turn_off(self):
        for dds in self.ddses:
            dds.init()
            dds.sw.on()
            dds.sw.off()
        self.trigger_ttl.off()
        self.core.reset()
    @kernel                                                      # noqa F405
    def init_dds(self):
        for dds in self.ddses:
            dds.init()
    @kernel                                                      # noqa F405
    def run(self):
        self.core.reset()
        self.init_dds()
        self.urukul1_ch0.set_att(self.att_397*dB)
        self.urukul1_ch1.set_att(self.att_866*dB)
        delay(5*ms)                                              # noqa F405
        while True:
            self.core.break_realtime()
            # with parallel:                                       # noqa F405
            #     self.run_doppler_cooling()
            delay(0.5*us)
            self.trigger_ttl.off()
            for i in range(self.rep):
                # self.core.break_realtime()
                self.run_397_photon_generation()
                with parallel:
                    self.run_trigger(n=1, unit=us)
                    self.run_866_photon_generation()
                delay(2.5*us)                                     # noqa F405
