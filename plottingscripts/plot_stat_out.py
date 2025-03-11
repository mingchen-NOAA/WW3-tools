import numpy as np
import matplotlib.pyplot as plt

from emcpy.plots.plots import LinePlot
from emcpy.plots.create_plots import CreatePlot, CreateFigure


day=[ 1.,  2.,  3.,  4.,  5.,  6.,  7.,  8.,  9., 10., 11., 12., 13., 14., 15., 16.]
rmse_hs_HR3a_summer_JASON3=[5.67960956, 5.84203492, 5.87713015, 6.00575437, 6.04385546, 6.097971,
 6.16729711, 6.17948412, 6.26397352, 6.25938725, 6.31635356, 6.35664655,
 6.39075575, 6.40988661, 6.39857877, 6.41306104]


lp = LinePlot(day, rmse_hs_HR3a_summer_JASON3)
plt_list = [lp]
plot1 = CreatePlot()
plot1.plot_layers = [lp]
figname='test.png'
fig = CreateFigure()
fig.plot_list = [plot1]
fig.create_figure()
fig.save_figure(figname)    
fig.close_figure()
