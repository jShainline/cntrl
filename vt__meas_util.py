import numpy as np
import time

def run_iv_sweep_srs__current_bias(voltage_source,voltage_meter,current_bias_values,R_series, delay = 0.75):
    
    vs = voltage_source
    dmm = voltage_meter
    
    vs.reset()
    vs.set_output(True)
    time.sleep(2)
    V = []
    I = []
    
    voltage_values = current_bias_values*R_series
    
    for v in voltage_values:
        
        vs.set_voltage(v)
        time.sleep(delay)
#        v1 = dmm.read_voltage(channel = 1)
        v1 = v
        v2 = dmm.read_voltage(channel = 2)
        v3 = dmm.read_voltage(channel = 3)
        V.append(v3)
        I.append((v1-v2)/R_series)
        
    vs.set_voltage(0)
    
    return np.array(V),np.array(I)