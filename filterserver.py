# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import socket
import pickle
import struct
import logging

try:
    from scipy import signal
except ImportError:
    pass

PARAM_FLAG = 'A'
DATA_FLAG = 'B'
END_FLAG = 'ENDIT'
QUIT_FLAG = 'ALLDONE'
RESET_FLAG = 'RESET'
ERR_FLAG = 'ERR'
RESET_FLAG = 'RESET'
OK_FLAG = 'ALLCLEAR'

logging.getLogger().setLevel(logging.INFO)

class FilterBase(object):
    buf = 4096
    
    def recvall(self, sock):
        d = []
        while True:
            d2 = sock.recv(self.buf)
            d.append(d2)
            if END_FLAG in d2:
                d[-1] = d2[:d2.find(END_FLAG)]
                break
        d = ''.join(d)
        logging.info('Received %i bytes' % len(d))
        #logging.debug('Received: "%s"' % d)
        return d

class FilterServer(FilterBase):
    
    def __init__(self, host='', port=50001, buf=4096):
        self.host = host
        self.port = port
        self.buf = buf
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.bind((self.host, self.port))
        self._s.listen(1)
        self.connect()
        
    def connect(self):
        logging.info('Accepting connections on port %i' % self.port)
        self.conn, addr = self._s.accept()
        logging.info('Connection from %s on port %i' % addr)
     
    def get_parameters(self):
        d = self.recvall(self.conn)
        try:
            interval, cutoff_freq, n = pickle.loads(d)
        except KeyError:
            self.conn.sendall(ERR_FLAG + END_FLAG)

        nyq_rate = 0.5/interval
        self.taps = signal.firwin(n, cutoff_freq/nyq_rate, window='hamming')
        logging.info('Received parameters: interval=%e, cutoff=%i, n=%i' % (interval, cutoff_freq, n))
        self.conn.sendall(OK_FLAG + END_FLAG)

    def process(self):
        d = self.recvall(self.conn)
        try:
            data = pickle.loads(d)
        except KeyError:
            self.conn.sendall(ERR_FLAG + END_FLAG)
        logging.info('Received data')
        data_f = signal.lfilter(self.taps, 1, data)
        logging.info('Returning filtered data')
        self.conn.sendall(pickle.dumps(data_f) + END_FLAG)

    def shutdown(self):
        if self.conn:
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()
        self._s.shutdown(socket.SHUT_RDWR)
        self._s.close()

    def run(self):
        while True:
            d = self.recvall(self.conn)
            if d == PARAM_FLAG:
                self.get_parameters()
            elif d == DATA_FLAG:
                self.process()
            elif d == RESET_FLAG:
                logging.info('Resetting.')
                self.connect()
            elif d == QUIT_FLAG:                
                self.shutdown()
                break


class FilterClient(FilterBase):
    
    def __init__(self, host, port=50001, buf=4096):
        self.host = host
        self.port = port
        self.buf = buf
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect((host, port))
        logging.info('Connected to %s on port %i' % (host, port))
    
    def set_parameters(self, interval, cutoff, n=101):
        self._s.sendall(PARAM_FLAG + END_FLAG)
        d = pickle.dumps((interval, cutoff, n))
        self._s.sendall(d + END_FLAG)
        r = self.recvall(self._s)
        if r == ERR_FLAG:
            raise FilterError('Setting parameters failed')
        else:
            logging.info('Parameters set')

    def filter(self, data):
        self._s.sendall(DATA_FLAG + END_FLAG)
        d = pickle.dumps(data)
        self._s.sendall(d + END_FLAG)
        r = self.recvall(self._s)
        if r == ERR_FLAG:
            raise FilterError('Error during filtering')
            
        data_f = pickle.loads(r)
        return data_f

    def disconnect(self):
        self._s.sendall(RESET_FLAG + END_FLAG)
        self.close()

    def quit_server(self):
        self._s.sendall(QUIT_FLAG + END_FLAG)
        self.close()
        
    def close(self):
        self._s.shutdown(socket.SHUT_RDWR)
        self._s.close()
    

class FilterError(Exception):
    pass

