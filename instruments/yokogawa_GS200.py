import visa

class yokogawa_GS200(object):
    """Python class for a Yokogawa GS200 voltage/current source instrument interface,
    written by Jeff Shainline, adapted from Adam McCaughan's generic example
    """
    def __init__(self, visa_name):
        self.rm = visa.ResourceManager()
        self.pyvisa = self.rm.open_resource(visa_name)
        self.pyvisa.timeout = 5000 # Set response timeout (in milliseconds)
        # self.pyvisa.query_delay = 1 # Set extra delay time between write and read commands

    def read(self):
        return self.pyvisa.read()
    
    def write(self, string):
        self.pyvisa.write(string)

    def query(self, string):
        return self.pyvisa.query(string)

    def close(self):
        self.pyvisa.close()
        
    def reset(self):
        self.write('*RST')

    def identify(self):
        return self.query('*IDN?')
