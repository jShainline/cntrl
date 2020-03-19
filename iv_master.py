#%% init
import sys
import os
import numpy as np
import time
import pickle
from matplotlib import pyplot as plt
from pylab import *

#%% set python path

working_dir = r'C:\Users\jms4\Documents\GitHub\cntrl'
dir1 = os.path.join(working_dir,'instruments')
dir2 = os.path.join(working_dir,'functions')
#dir3 = os.path.join(working_dir,'measurement')

if working_dir not in sys.path:
    sys.path.append(working_dir)
    sys.path.append(dir1)
    sys.path.append(dir2)
#    sys.path.append(dir3)
    
#%% using sim900, sweep current, read voltage (can be used for 2-wire or 4-wire)
from utilities import iv__sim900__sweep_current__read_voltage, iv__fit_to_line

current_range = [-100e-6,100e-6]
current_step = 10e-6
measurement_delay = 0.75
bias_resistance = 100e3;#must be much larger than device under test to ensure voltage source is acting like current source

#measure
current_applied_vec, voltage_read_vec = iv__sim900__sweep_current__read_voltage(current_range,current_step,bias_resistance,measurement_delay)

#fit to line
slope, current_vec_dense, voltage_read_vec_fit = iv__fit_to_line(current_applied_vec,voltage_read_vec)

#plot      
fig, axes = plt.subplots(1,1)
axes.plot(voltage_read_vec_fit,current_vec_dense*1e6, 'o-', linewidth = 1, markersize = 3, label = 'fit'.format(1))
axes.plot(voltage_read_vec,current_applied_vec*1e6, 'o-', linewidth = 1, markersize = 3, label = 'resistor'.format(1))
axes.set_xlabel(r'Voltage [V]', fontsize=20)
axes.set_ylabel(r'Current [uA]', fontsize=20)

#ylim((ymin_plot,ymax_plot))
#xlim((xmin_plot,xmax_plot))

axes.legend(loc='best')
grid(True,which='both')
title('Resistance = '+str(slope)+' ohm')
plt.show()

time.sleep(1) 

#%% using sim900, measure transistor


