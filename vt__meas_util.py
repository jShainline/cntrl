import numpy as np
import time

def run_iv_sweep_srs__current_bias(voltage_source,voltage_meter,voltage_meter_channel,current_bias_values,R_series, delay = 0.75):
    
    vs = voltage_source
    dmm = voltage_meter
    
    vs.reset()
    vs.set_output(True)
    time.sleep(2)
    V = []
    I = []
    
    voltage_values = current_bias_values*R_series
    
    print('running I-V sweep ...')
    for v in voltage_values:
        
        print('v = '+str(v)+' of '+str(voltage_values[-1]))
        vs.set_voltage(v)
        time.sleep(delay)
        V.append(dmm.read_voltage(channel = voltage_meter_channel))
#        I.append((v1-v2)/R_series)
        
    vs.set_voltage(0)
    
    return np.array(V)