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
from time import sleep
import Adafruit_DHT
from Publisher import Publisher
import subprocess

try:
    import serial
except:
    print 'Some dependendencies are not met'
    print 'You need to install the pyserial package'
    print 'install them via pip'
    sys.exit()




class SerialData(object):
    """ This class handles the communication with Arduino Boards.
    """
    def __init__(self, port='/dev/ttyACM1'):
        signal.signal(signal.SIGINT, self.signal_handler)
        self.__publisher = Publisher()
        self.__last_received = '{"temperature":"-100","humidity":"-100"}'
        self.__kill_received = False
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
            self.__thread = Thread(target=self.__receiving, args=(self.ser,)).start()

    def __receiving(self, ser):
        readline = ''
        while not self.__kill_received:
            if self.__kill_received:
                logging.debug('got kill')
            readline = ser.readline()
            if readline != '':
                self.__last_received = readline
                self.__publisher.publish(self.__last_received)

    def next(self):
        if not self.ser:
            return 100  # return anything so we can test when Arduino isn't connected
        for j in range(40):
            raw_line = self.__last_received
            try:
                # logging.debug(raw_line.strip())
                return raw_line.strip()
            except ValueError, e:
                # print 'bogus data',raw_line
                logging.debug("Value Error: {0}".format(raw_line.strip()))
                print str(e)
                time.sleep(.005)
        return 0.

    def signal_handler(self, signal, frame):
        kill_received = True
        os._exit(1)

    def __del__(self):
        if self.ser:
            self.ser.close()

class RPData(object):
    """This class handles hardware communication with sensors and actuators directly attached to
    the RPi
    """
    def __init__(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        self.__lastswitchstate = 1;
        self.__temperature = -100;
        self.__humidity = 0;
        self.__thread = Thread(target=self.__receiving).start()
        self.__kill_received = False
        self.__publisher = Publisher()

    def __receiving(self):
        """This function is called by the thread to update the device"""
        while not self.__kill_received:
            if self.__kill_received:
                logging.debug("Thread got killed")
            humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 4)
            logging.debug("Got temperature reading: "+str(temperature)+" and also got Humidity reading: "+str(humidity))
            if self.__temperature != temperature or self.__humidity != humidity:
                if self.__humidity != 0 and self.__temperature != -100:
                    self.__publisher.publish({"temperature":temperature,"humidity":humidity, "switch":self.__lastswitchstate})
                self.__humidity = humidity
                self.__temperature = temperature
            sleep(2)

    def next(self):
        return str('{"temperature":"%5.2f","humidity":"%5.2f", "switch":"%d"}' % (self.__temperature, self.__humidity, self.__lastswitchstate))

    def updateSwitch(self, state):
        subprocess.call(["sudo", "/usr/local/bin/send433", "11111", "11", str(state)])
        self.__lastswitchstate = state

    def signal_handler(self, signal, frame):
        self.__kill_received = True
        os._exit(1)


if __name__ == '__main__':
    s = SerialData()

    for i in range(10):
        time.sleep(1)
        print s.next()

