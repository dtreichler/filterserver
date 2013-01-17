filterserver
============

Simple python socket server-client module to apply scipy.signal.lfilter to some data


Usage
=====

Module should be used on both client and server ends.

Server
------
```python
from filterserver import *
 
s = FilterServer(host='', port=50001, buf=4096)
s.run()
```

Creates a server object listening on all connections on port 50001. `buf` is the chunk size to read from the socket. Should be a relatively low power of 2. All arguments are optional.

Client
------

```python
from pylab import *
from filterserver import *

# Create some data
interval = 1e-6 # time step
t = arange(0, 5e-3, interval)
y_d = 2*sin(2*pi*t) # Signal
noise = 5*randn(t.shape[0]) # Noise
y = y_d + noise

c = FilterClient(host='nas', port=50020, buf=4096)
cutoff = 5000 # Cutoff frequency for low-pass filter
N = 201 # Window size
c.set_parameters(interval, cutoff, N)
y_f = c.filter(y)
t_f = t - 0.5*(N-1)*interval # Account for time shift due to filtering

fig = figure()
ax = fig.add_subplot(111)
ax.plot(t,y,'r',t_f,y_f,'g',t,y_d,'b')
```

Arguments for `FilterClient` are similar to `FilterServer`. Only the `host` argument is required.