from spikeylab.io.players import ContinuousPlayer
from spikeylab.main.protocol_acquisition import Experimenter
from spikeylab.tools.util import increment_title

class ChartExperimenter(Experimenter):
    def __init__(self, signals):
        Experimenter.__init__(self, signals)

        self.chart_name = 'chart_0'
        save_data = False
        self.player = ContinuousPlayer()
        self.player.set_read_function(self.emit_ncollected)

    def _initialize_run(self):
        self.player.set_aochan(self.aochan)

    def start_chart(self):
        """Begin on-going chart style acqusition"""
        self.current_dataset_name = self.chart_name
        self.datafile.init_data(self.current_dataset_name, mode='continuous')
        self.chart_name = increment_title(self.chart_name)
        
        # stimulus tracker channel hard-coded at least chan for now
        self.player.start_continuous([self.aichan, u"PCI-6259/ai31"])

    def stop_chart(self):
        self.player.stop_all()
        self.datafile.consolidate(self.current_dataset_name)

    def emit_ncollected(self, data):
        # relay emit signal
        response = data[0,:]
        stim_recording = data[1,:]
        self.signals.ncollected.emit(stim_recording, response)
        if self.save_data:
            self.datafile.append(self.current_dataset_name, response)

    def _initialize_test(self, test):
        pass

    def _process_response(self, response, trace_info, irep):
        pass