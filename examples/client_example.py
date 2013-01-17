from pylab import *
from filterserver import *

# Create some data
interval = 1e-6 # time step
t = arange(0, 5e-3, interval)
y_d = 2*sin(2*pi*t) # Signal
noise = 5*randn(t.shape[0]) # Noise
y = y_d + noise

c = FilterClient(host='nas', port=50025, buf=4096)
cutoff = 5000 # Cutoff frequency for low-pass filter
N = 201 # Window size
c.set_parameters(interval, cutoff, N)
y_f = c.filter(y)
t_f = t - 0.5*(N-1)*interval # Account for time shift due to filtering

fig = figure()
ax = fig.add_subplot(111)
ax.plot(t,y,'r',t_f,y_f,'g',t,y_d,'b')
