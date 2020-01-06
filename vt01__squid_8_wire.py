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

#import functions
from vt__meas_util import run_iv_sweep_srs__current_bias


#%% measurement specifics


#squid ports
incoil_v_source_srs = vs1
squid_v_source_srs = vs2
addflux_v_srs = vs3
squid_v_meas_srs = dmm
squid_v_meas_srs_dmm_channel = 4

dmm.set_impedance(gigaohm=True, channel = squid_v_meas_srs_dmm_channel)

#resistors in series with voltage sources
incoil_i_source_res = 1e4
squid_i_source_res = 1e4
addflux_i_source_res = 1e4

#%% get squid I-V in the absence of flux
current_bias_values = np.arange(0,300e-6,3e-6)
V = run_iv_sweep_srs__current_bias(squid_v_source_srs,squid_v_meas_srs,squid_v_meas_srs_dmm_channel,current_bias_values,squid_i_source_res, delay = 0.75)
    
I = current_bias_values
fig, axes = plt.subplots(1,1)
axes.plot(I*1e6,V*1e3,label = '1')
axes.set_ylabel(r'Voltage across SQUID (mV)', fontsize=20)
axes.set_xlabel(r'Current applied to SQUID (uA)', fontsize=20)

#ylim((ymin_plot,ymax_plot))
#xlim((xmin_plot,xmax_plot))

axes.legend(loc='best')
grid(True,which='both')
plt.show()

p = np.polyfit(I,V,1)
print('%0.1f Ohm' % (p[0]))

title(str(np.around(p[0],decimals = 2))+' ohm')

#%% measure SQUID voltage as a function of incoil current for several values of SQUID current bias



