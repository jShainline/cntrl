#%%

# Heater measurement code
# Run add_path.py first
from amcc.instruments.rigol_dg5000 import RigolDG5000
from amcc.instruments.lecroy_620zi import LeCroy620Zi
from amcc.instruments.switchino import Switchino
from amcc.instruments.tektronix_awg610 import TektronixAWG610
from amcc.instruments.srs_sim970 import SIM970
from amcc.instruments.srs_sim928 import SIM928
from amcc.instruments.agilent_53131a import Agilent53131a

from amcc.standard_measurements.ic_sweep import setup_ic_measurement_lecroy, run_ic_sweeps, calc_ramp_rate
from tqdm import tqdm # Requires "colorama" package also on Windows to display properly
import numpy as np
import pandas as pd
import numpy as np
import time
import pickle
import datetime
from matplotlib import pyplot as plt


import itertools
def parameter_combinations(parameters_dict):
    for k,v in parameters_dict.items():
        try: v[0]
        except: parameters_dict[k] = [v]
    value_combinations = list(itertools.product(*parameters_dict.values()))
    keys = list(parameters_dict.keys())
    return [{keys[n]:values[n] for n in range(len(keys))} for values in value_combinations]

def plot_2d_counts_vs_bias(data, max_count_ratio = 2):
    # Plot 2D (Pulse voltage)  vs (Pulse length), where color = vdmm (latching or not)
    dfall = pd.DataFrame(data)
    for ports, df in dfall.groupby('ports'):
#        for vbias, df in df2.groupby('vbias'):
#        ibias = vbias/df['rbias'].unique()[0]
        fig, ax = plt.subplots()
#        ax.set_xscale('log')
#        ax.set_yscale('log')
        dfp = df.pivot('ibias_readout', 'ibias_snspd', 'count_ratio')
        #X,Y = np.meshgrid()
        im = ax.pcolor(np.array(dfp.columns)*1e6, np.array(dfp.index)*1e6, np.ma.masked_invalid(dfp),
                       vmin = 0, vmax = max_count_ratio)
        ax.patch.set(hatch='x', edgecolor='lightgray')
        cbar = fig.colorbar(im)
        cbar.ax.set_ylabel('(readout counts) / (SNSPD counts)')
#            plt.clim(color_range)
        plt.xlabel('Ibias SNSPD (uA)')
        plt.ylabel('Ibias Readout nw (uA)')
        plt.title('Count ratio vs bias (Ports %s)' % [ports])
        plt.tight_layout()
        filename = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S-') + ('ports ' + str(ports))
        plt.savefig(filename + '.png')
#        pickle.dump(fig, open(filename + '.fig.pickle', 'wb'))
    #    pickle.dump({'data':data}, open(filename + '.pickle', 'wb'))
    
    

def tci_readout_counts_vs_bias(
    vbias_snspd = 0.5,
    vbias_readout = 0.5,
    rbias = 10e3,
    count_time = 0.1,
    ports = None,
    **kwargs,
    ):
    
    # Switch select
    global last_ports
    if ports is not None:
        if last_ports != ports:
            switch.select_ports(port_pair = ports)
            time.sleep(1)
            last_ports = ports
    
    ibias_readout = vbias_readout/rbias
    ibias_snspd = vbias_snspd/rbias
    
    vs1_snspd.set_voltage(vbias_snspd)
    vs2_readout.set_voltage(vbias_readout)
    time.sleep(0.15)
    counter1_snspd.write(':INIT')
    counter2_readout.write(':INIT')
    time.sleep(count_time+0.1)
    count_rate_snspd = float(counter1_snspd.query('FETCH?'))
    count_rate_readout = float(counter2_readout.query('FETCH?'))
    if count_rate_snspd == 0:
        count_ratio = np.nan
    else:
        count_ratio = count_rate_readout/count_rate_snspd
    vs1_snspd.set_voltage(0)
    vs2_readout.set_voltage(0)
    time.sleep(0.05)
    
    data = locals()
    
    return data


#%%============================================================================
# Setup instruments
#==============================================================================

#lecroy = LeCroy620Zi("TCPIP::%s::INSTR" % '192.168.1.100')
#awg = RigolDG5000('USB0::0x1AB1::0x0640::DG5T171200124::INSTR')
switch = Switchino('COM7')

counter1_snspd = Agilent53131a('GPIB0::12::INSTR')
counter2_readout = Agilent53131a('GPIB0::10::INSTR')
vs1_snspd = SIM928('GPIB0::4', 3)
vs2_readout = SIM928('GPIB0::4', 4)


#%%============================================================================
# TCI counts vs bias measurement setup
# 
# For nonlatching devices - The bias is constant.  The bias is set for both
# the readout nanowire and the SNSPD, then counts vs time are measured
# Switch 1 / Counter 1 = SNSPD
# Switch 2 / Counter 2 = Readout
#==============================================================================

trigger_voltage = 0.05
count_time = 0.1

# Setup counter
# Setup parameters
for c in [counter1_snspd,counter2_readout]:
    c.reset()
    time.sleep(0.1)
    c.basic_setup()
    c.set_impedance(ohms = 50, channel = 1)
    c.setup_timed_count(channel = 1)
    c.set_100khz_filter(False, channel = 1)
    c.set_trigger(trigger_voltage = trigger_voltage, slope_positive = True, channel = 1)
    c.set_hysteresis(100)
    c.timed_count(counting_time = count_time)

#%% 2D mapping
global last_ports
last_ports = None

parameters_dict = dict(
        ports = [(2,1),(4,3)], #   [(2,1),(4,3),(6,5),(8,7),(10,9)]
#        ports = [(1,2),(3,4),(7,8),(9,10)], #    [(1,2),(3,4),(5,6),(7,8),(9,10)]
#        ports = [(10,9)], # (8,7), (10,9),
        vbias_readout = np.linspace(0.0,4.5,21),
#        vbias_readout = [0],
        vbias_snspd = np.linspace(0.0,3,21),
        rbias = 100e3,
        count_time = count_time,
        trigger_voltage = trigger_voltage,
        ) # Lowest variable is fastest-changing index


parameter_combos = parameter_combinations(parameters_dict)
print(len(parameter_combos))

vs1_snspd.set_output(True)
vs2_readout.set_output(True)
data = []
for pc in tqdm(parameter_combos):
    print(list(pc.values()))
    data.append(tci_readout_counts_vs_bias(**pc))
switch.disable()

filename = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
pickle.dump({'data':data}, open(filename + '.pickle', 'wb'))
plot_2d_counts_vs_bias(data)


#%% Plotting counts vs bias with readout on and off
global last_ports
last_ports = None

parameters_dict = dict(
        ports = [(10,9)],
        vbias_snspd = [0,2.5],
        vbias_readout = np.linspace(0.0,4,101),
        rbias = 100e3,
        count_time = count_time,
        trigger_voltage = trigger_voltage,
        ) # Lowest variable is fastest-changing index


parameter_combos = parameter_combinations(parameters_dict)
print(len(parameter_combos))

vs1_snspd.set_output(True)
vs2_readout.set_output(True)
data = []
for pc in tqdm(parameter_combos):
    print(list(pc.values()))
    data.append(tci_readout_counts_vs_bias(**pc))
switch.disable()

filename = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
pickle.dump({'data':data}, open(filename + '.pickle', 'wb'))


# Plot snspd counts for a few readout bias values
df = pd.DataFrame(data)
plt.figure();
for name,group in df.groupby('ports'):
    for name2,group2 in group.groupby('ibias_readout'):
        label = 'Ports %s / Ir = %0.1f uA' % (str(name), name2*1e6)
        if name2 == 0: marker = 'x'
        else: marker = '.'
        x = group2.ibias_snspd*1e6
        y = group2.count_rate_snspd/np.quantile(group2.count_rate_snspd, 0.9)
        plt.plot(x,y, marker, label = label)
plt.xlabel('Isnspd (uA)')
plt.xlabel('Normalized counts')
plt.legend()
plt.tight_layout()
filename = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S-')
plt.savefig(filename + '.png')


## Plot readout counts for a few snspd bias values
#df = pd.DataFrame(data)
#plt.figure();
#for name,group in df.groupby('ports'):
#    for name2,group2 in group.groupby('ibias_snspd'):
#        if name2 == 0: marker = 'x'
#        else: marker = '.'
#        x = group2.ibias_readout*1e6
#        y = group2.count_rate_readout
#        plt.plot(x,y, marker, label = ('Readout counts / Isnspd = %0.1f uA' % (name2*1e6)))
#        x = group2.ibias_readout*1e6
#        y = group2.count_rate_snspd
#        plt.plot(x,y, marker, label = ('SNSPD counts / Isnspd = %0.1f uA' % (name2*1e6)))
#plt.xlabel('Ireadout (uA)')
#plt.ylabel('Readout counts (norm)')
#plt.legend()
#plt.tight_layout()
#filename = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S-')
#plt.savefig(filename + '.png')



#%%

df = pd.DataFrame(data)
# Plotting dependence of SNSPD counts on readout bias conditions
figure();
for name, group in df.groupby(df.ibias_snspd):
    plot(group.ibias_readout*1e6, group.count_rate_snspd,'.-', label = str(np.round(name*1e6,1)) + ' uA')
legend()
xlabel('SNSPD bias (uA)')
ylabel('Counts (1/s)')
plt.title('SNSPD count rate vs bias\nVarying readout current')


figure();
df2 = df[df.ibias_readout == 4.30e-05]
plot(df2.ibias_snspd*1e6, df2.count_rate_snspd,'.-')
xlabel('Readout bias (uA)')
ylabel('Count rate (1/s)')
