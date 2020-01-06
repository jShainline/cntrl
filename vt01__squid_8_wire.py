#%% initialization
import numpy as np
from pylab import *

# Import instruments
from amcc.instruments.srs_sim970 import SIM970
from amcc.instruments.srs_sim928 import SIM928
from amcc.instruments import Switchino

# Setup instruments
dmm = SIM970('GPIB0::4', sim900port = 7)
vs1 = SIM928('GPIB0::4', sim900port = 3)
vs2 = SIM928('GPIB0::4', sim900port = 4)
vs3 = SIM928('GPIB0::4', sim900port = 5)
switch = Switchino('COM7')

dmm.set_impedance(gigaohm=False, channel = 2)
dmm.set_impedance(gigaohm=False, channel = 3)

#import functions
from vt__meas_util import run_iv_sweep_srs__current_bias


#%% measurement specifics


#squid ports
incoil_v_source_srs = vs1
squid_v_source_srs = vs2
addflux_v_srs = vs3
squid_v_meas_srs = dmm

#resistors in series with voltage sources
incoil_i_source_res = 1e4
squid_i_source_res = 1e4
addflux_i_source_res = 1e4

#%% get squid I-V in the absence of flux
current_bias_values = np.arange(0,300e-6,30e-6)
V,I = run_iv_sweep_srs__current_bias(squid_v_source_srs,squid_v_meas_srs,current_bias_values,squid_i_source_res, delay = 0.75)
    
fig, axes = plt.subplots(1,1)
axes.plot(V*1e3,I*1e6,label = '1')
axes.set_xlabel(r'Voltage (mV)', fontsize=20)
axes.set_ylabel(r'Current (uA)', fontsize=20);
axes.legend(loc='best')
grid(True,which='both')
plt.show()
#title(str(port_pair))

#%%
#def iv(port_pair = [1,2], voltages = np.linspace(0,1,25),
#             R_series = 10e3, delay = 0.75):
#    switch.select_ports(port_pair = port_pair)
#    V, I = run_iv_sweep_srs(voltages, R_series, delay = delay)
#    return V, I
#
#
#port_pairs = [
#        [1,2],
#        [5,6],
#        ]
#for port_pair in port_pairs:
#    voltages = np.linspace(0,1,15)
#    V, I = iv(port_pair = port_pair, voltages = voltages, R_series = 10e3, delay = 1.5)
#    
#    figure()
#    plot(V*1e3,I*1e6,'.')
#    xlabel('Voltage (mV)')
#    ylabel('Current (uA)')
#    title(str(port_pair))
#
#    p = np.polyfit(I,V,1)
#    print(port_pair)
#    print('%0.1f Ohm' % (p[0]))
