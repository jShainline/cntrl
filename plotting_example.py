from pylab import *

fig, axes = plt.subplots(1,1)
axes.loglog(numConnections_vec[:],numNeurons_mat[0,:],label = '2 planes')
axes.loglog(numConnections_vec[:],numNeurons_mat[1,:],label = '6 planes')
axes.loglog(numConnections_vec[:],numNeurons_mat[2,:],label = '18 planes')
axes.loglog(numConnections_vec[:],numConnections_vec[:],label = 'numNeuron = numConn')
axes.loglog(numConnections_vec[:],10*numConnections_vec[:],label = 'numNeuron = 10 numConn')
axes.loglog(numConnections_vec[:],100*numConnections_vec[:],label = 'numNeuron = 100 numConn')
axes.legend()
axes.set_xlabel(r'connections per neuron', fontsize=20)
axes.set_ylabel(r'num neurons on 300 mm wafer', fontsize=20);
ylim((ymin_plot,ymax_plot))
xlim((xmin_plot,xmax_plot))
axes.legend(loc='best')
grid(True,which='both')
show()