import numpy as np
import time
from datetime import datetime
import warnings
import os
import inspect 

#%%
def iv__sim900__sweep_current__read_voltage(current_range,current_step,bias_resistance,measurement_delay):
    
    if np.abs(current_applied_vec[0]) >= 0.01 or np.abs(current_applied_vec[-1]) >= 0.01:
        warnings.showwarning('The SIM928 can only output in the range [-10,10]mA. You have attempted to exceed this range.',UserWarning,os.path.basename(__file__),inspect.currentframe().f_back.f_lineno)
    
    from instruments.srs_sim970 import SIM970
    from instruments.srs_sim928 import SIM928
    
    voltage_meter = SIM970('GPIB0::2',7)#voltmeter = SIM970(visa_name = 'GPIB0::2', sim900port = 2)
    voltage_source = SIM928('GPIB0::2', 5)
    
    current_applied_vec = np.arange(current_range[0],current_range[1]+current_step,current_step)
    #SIM928 max voltage = [-20,20]V
    voltage_applied_vec = current_applied_vec*bias_resistance
    if np.abs(voltage_applied_vec[0]) >= 20 or np.abs(voltage_applied_vec[-1]) >= 20:
        warnings.showwarning('The SIM928 can only output in the range [-20,20]V. You have attempted to exceed this range.',UserWarning,os.path.basename(__file__),inspect.currentframe().f_back.f_lineno)
    
    voltage_read_vec = []
    voltage_source.reset()
    voltage_source.set_output(True)
    for ii in range(len(voltage_applied_vec)):
        voltage_source.set_voltage(voltage = voltage_applied_vec[ii])
        time.sleep(measurement_delay)
        voltage_read_vec.append(voltage_meter.read_voltage(channel = 1))
    voltage_source.set_output(False)

    return current_applied_vec, voltage_read_vec

def iv__fit_to_line(current_applied_vec,voltage_read_vec):
    
    p = np.polyfit(current_applied_vec,voltage_read_vec,1)
    current_vec_dense = np.linspace(current_applied_vec[0],current_applied_vec[-1],1000)
    voltage_read_vec_fit = np.polyval(p,current_vec_dense)

    return p[0], current_vec_dense, voltage_read_vec_fit

def flux_purge_srs(voltage_source,r_series,desired_current,hold_time):
    
    print('\n\npurging flux ...')
    vs = voltage_source
    v = desired_current*r_series
    vs.set_voltage(v)
    print('beginning hold time ...')
    time.sleep(hold_time)
    print('ending hold time ...')
    vs.set_voltage(0)
    
    return


def iv_sweep_srs__current_bias(voltage_source,voltage_meter,voltage_meter_channel,current_bias_values,r_series, delay = 0.75,device_name = 'vt01'):
    
    vs = voltage_source
    dmm = voltage_meter
    
    vs.reset()
    vs.set_output(True)
    time.sleep(2)
    V = []
    
    voltage_values = current_bias_values*r_series
    
    print('\n\nrunning I-V sweep ...')
    vs.set_voltage(0)
    now = datetime.now()
    file_name = device_name+'__IV__'+now.strftime('%H_%M_%S')+'.dat'
    f = open(file_name,'w+')
    f.write('applied current, measured voltage\n')
    for ii in range(len(voltage_values)):
        
        v = voltage_values[ii]
        print('ii = {0} of {1}'.format(ii+1,len(voltage_values)))
        vs.set_voltage(v)
        time.sleep(delay)
        V.append(dmm.read_voltage(channel = voltage_meter_channel))
        f.write('{0}, {1}\n'.format(current_bias_values[ii],V[ii]))
#        I.append((v1-v2)/R_series)
        
    vs.set_voltage(0)
    
    f.close()
    
    return np.array(V)


def sq_voltage_vs_incoil_current(sq_voltage_source,sq_source_r_series,sq_voltage_meter,sq_voltage_channel,incoil_voltage_source,incoil_r_series,sq_current_bias_values,incoil_current_bias_values,delay,device_name):
    
    vs1 = sq_voltage_source
    vs2 = incoil_voltage_source
    vs1.reset()
    vs1.set_output(True)
    time.sleep(1)
    vs2.reset()
    vs2.set_output(True)
    time.sleep(1)
    
    dmm = sq_voltage_meter
    
    I_sq_bias = np.array(sq_current_bias_values)
    I_incoil_current = np.array(incoil_current_bias_values)
    V_sq_meas = np.zeros((len(I_incoil_current),len(I_sq_bias)))
    
    voltage_values_sq = I_sq_bias*sq_source_r_series
    voltage_values_incoil = I_incoil_current*incoil_r_series
    
    print('\n\nrunning incoil sweep ...\n')
        
    vs1.set_voltage(0)
    vs2.set_voltage(0)
    
    now = datetime.now()
    file_name = device_name+'__incoil_sweep__'+now.strftime('%H_%M_%S')+'.dat'
    f = open(file_name,'w+')    
    for ii in range(len(voltage_values_sq)):
        
        print('\n\nsquid current bias {0} of {1}\n'.format(ii+1,len(voltage_values_sq)))
        
        v1 = voltage_values_sq[ii]
        vs1.set_voltage(v1)
        f.write('sq bias current\n')
        f.write('{0}\n'.format(sq_current_bias_values[ii]))
        f.write('incoil current, measured sq voltage\n')
        time.sleep(delay)
        
        for jj in range(len(voltage_values_incoil)):
            
            print('incoil current bias {0} of {1}'.format(jj+1,len(voltage_values_incoil)))
            
            v2 = voltage_values_incoil[jj]
            vs2.set_voltage(v2)
            time.sleep(delay)
            
            V_sq_meas[jj,ii] = dmm.read_voltage(channel = sq_voltage_channel)
            f.write('{0}, {1}\n'.format(incoil_current_bias_values[jj],V_sq_meas[jj,ii]))
    
    vs1.set_voltage(0)
    vs2.set_voltage(0)
    
    return I_sq_bias,I_incoil_current,V_sq_meas