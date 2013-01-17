from filterserver import *

s = FilterServer(host='', port=50025, buf=4096)
s.run()
