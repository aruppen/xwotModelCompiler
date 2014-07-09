"""
Listen to serial, return most recent numeric values
Lots of help from here:
http://stackoverflow.com/questions/1093598/pyserial-how-to-read-last-line-sent-from-serial-device
"""
from threading import Thread
import time
import logging
import signal
import sys
import os

try:
    import serial
except:
    print 'Some dependendencies are not met'
    print 'You need to install the pyserial package'
    print 'install them via pip'
    sys.exit()

last_received = '{"temperature":"-100","humidity":"-100"}'
kill_received = False


def receiving(ser):
    global last_received
    global kill_received
    buffer = ''
    while not kill_received:
        if kill_received:
            logging.debug('got kill')
        buffer = ser.readline()
        if buffer != '':
            last_received = buffer

class SerialData(object):
    def __init__(self, port='/dev/ttyACM1'):
        signal.signal(signal.SIGINT, self.signal_handler)
        try:
            self.ser =  serial.Serial(
                port=port,
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.1,
                xonxoff=0,
                rtscts=0,
                interCharTimeout=None
            )
        except serial.serialutil.SerialException:
            # no serial connection
            self.ser = None
        else:
            self.__thread = Thread(target=receiving, args=(self.ser,)).start()

    def next(self):
        if not self.ser:
            return 100  # return anything so we can test when Arduino isn't connected
        # return a float value or try a few times until we get one
        for j in range(40):
            raw_line = last_received
            try:
                # logging.debug(raw_line.strip())
                # map(float, raw_line.strip().split(','))
                return raw_line.strip()
            except ValueError, e:
                # print 'bogus data',raw_line
                logging.debug("Value Error: {0}".format(raw_line.strip()))
                print str(e)
                time.sleep(.005)
        return 0.

    def next_two(self):
        if not self.ser:
            return [100, 100]  # return anything so we can test when Arduino isn't connected
        # return a float value or try a few times until we get one
        for j in range(40):
            raw_line = last_received
            try:
                # logging.debug(raw_line.strip())
                return map(float, raw_line.strip().split(','))
            except ValueError, e:
                # print 'bogus data',raw_line
                logging.debug("Value Error: %s", raw_line.strip())
                logging.debug(str(e))
                time.sleep(.005)
        return [0., 0.]

    def signal_handler(self, signal, frame):
        kill_received = True
        os._exit(1)

    def __del__(self):
        if self.ser:
            self.ser.close()


if __name__ == '__main__':
    s = SerialData()

    for i in range(10):
        time.sleep(1)
        print s.next()

