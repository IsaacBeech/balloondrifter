# library dependencies
import time
#time.sleep(10) # warmuptime
from datetime import datetime
import asyncio
from picamera import PiCamera

from w1thermsensor import W1ThermSensor

import serial
import string
from pyubx2 import UBXReader

import RPi.GPIO as GPIO
import pigpio

import csv

class Balloon:
    def __init__(self, type):
        try:
            self.temp_sensor = W1ThermSensor()
        except:
            print("Temp sensor not connected")
            
        self.gpsport = "/dev/ttyS0"
        
        try:
            ser=serial.Serial(self.gpsport,baudrate=38400,timeout=0.5)
        except:
            print("GPS not connnected")
            
        self.ubr=UBXReader(ser)
        
        #class variables
        self.gps_lon = 0.0
        self.gps_lat = 0.0
        self.gps_height_raw = 0.0
        self.gps_height_MSL = 0.0
        self.gps_velN = 0.0
        self.gps_velE = 0.0
        self.gps_velD = 0.0
        self.gps_Nfix = 0
        
        self.temp = 0.0
        self.press = 0.0
        
        # frequencies
        self.gps_hz = 8
        self.temp_hz = 2
        self.press_hz = 4
        self.log_hz = 4
        self.camera_wait = 30*60 # 30 min in sec
        
        # Servo params
        self.releasePos = 1700
        self.holdPos = 1000
        self.releasePin1 = 18
        self.releasePin2 = 27
        
        #servo setup   
        self.pwm= pigpio.pi()
        self.pwm.set_mode(self.releasePin1, pigpio.OUTPUT)
        self.pwm.set_PWM_frequency(self.releasePin1, 50)
        self.pwm.set_servo_pulsewidth(self.releasePin1, self.holdPos)
        self.pwm.set_mode(self.releasePin2, pigpio.OUTPUT)
        self.pwm.set_PWM_frequency(self.releasePin2, 50)
        self.pwm.set_servo_pulsewidth(self.releasePin2, self.holdPos)
        time.sleep(1)
        
        #csv setup
        datapath = '/home/pi/Desktop/HAB/data/'
        if type == 'real': 
            filename = 'real.csv'
        elif type == 'ground':
            filename = 'groundtest.csv'
        else:
            filename = 'dump.csv'
            
        self.file = datapath+filename
        header = ['time', 'gps_lat', 'gps_lon', 'gps_height_raw', 'gps_height_MSL','gps_velN', 'gps_velE', 'gps_velD', 'gps_Nfix', 'temp_ds18b20', 'press']

        with open(self.file, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(header)
        
        # Camera setup
        self.camera = PiCamera()
        self.camfiles = ['/home/pi/Desktop/HAB/data/video/flightvid1.h264',
                    '/home/pi/Desktop/HAB/data/video/flightvid2.h264',
                    '/home/pi/Desktop/HAB/data/video/flightvid3.h264',
                    '/home/pi/Desktop/HAB/data/video/flightvid4.h264',
                    '/home/pi/Desktop/HAB/data/video/flightvid5.h264',
                    '/home/pi/Desktop/HAB/data/video/flightvid6.h264']
        
        return
    
    async def get_temp(self):
        print("temp started")
        while True:
            try:
                self.temp = self.temp_sensor.get_temperature() # celcius
            except:
                donothing=0
                #print('no valid temp')
            print("temp gathered")
            await asyncio.sleep(1/self.temp_hz)    
        
     
    async def get_gps(self):
        print("GPS Started")
        while True:
            try:
                (raw,newmsg) = self.ubr.read()
                if newmsg.identity == 'NAV-POSLLH':
                    self.gps_lat=newmsg.lat
                    self.gps_lon=newmsg.lon
                    self.gps_height_raw=newmsg.height
                    self.gps_height_MSL=newmsg.hMSL/1000
                        
                elif newmsg.identity == 'NAV-VELNED':
                    self.gps_velN = newmsg.velN
                    self.gps_velE = newmsg.velE
                    self.gps_velD = newmsg.velD
                        
                elif newmsg.identity =='NAV-STATUS':
                    self.gps_Nfix = newmsg.gpsFix
                        
                else:
                    print('invalid GPS message')
            except:
                print("GPS Error")
            
            print("GPS gathered")
            await asyncio.sleep(1/self.gps_hz)    
    
    async def get_press(self):
        while True:
            self.press=0
            await asyncio.sleep(1/self.press_hz)    
    
    def release1(self):
        self.pwm.set_servo_pulsewidth(self.releasePin1, self.releasePos)
        time.sleep(.1)
        return
    
    def release2(self):
        self.pwm.set_servo_pulsewidth(self.releasePin2, self.releasePos)
        time.sleep(.1)
        return
    
    def openrelease(self):
        self.pwm.set_servo_pulsewidth(self.releasePin1, self.holdPos)
        self.pwm.set_servo_pulsewidth(self.releasePin2, self.holdPos)
        time.sleep(.1)
        return
    
    def sweep_test(self):
        for dc in range(self.holdPos, self.releasePos, 10):
            self.pwm.set_servo_pulsewidth(self.releasePin1, dc)
            self.pwm.set_servo_pulsewidth(self.releasePin2, dc)
            #print(dc)
            time.sleep(.01)
        
        for dc in range(self.releasePos, self.holdPos, -10):
            self.pwm.set_servo_pulsewidth(self.releasePin1, dc)
            self.pwm.set_servo_pulsewidth(self.releasePin2, dc)
            #print(dc)
            time.sleep(.01)
        
        time.sleep(1)
        return
        
    async def camera(self):
        for x in self.camfiles:
            self.camera.start_recording(self.camfiles[x])
            await asyncio.sleep(self.camera_wait)
        
    
    async def logcsv(self):
        print("csv started")
        while True:
            now = datetime.now()
            time = now.strftime("%H:%M:%S")
            data = [time, self.gps_lat, self.gps_lon, self.gps_height_raw, self.gps_height_MSL, self.gps_velN, self.gps_velE, self.gps_velD, self.gps_Nfix, self.temp]
            
            with open (self.file, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(data)
            
            print("csv logged")
            await asyncio.sleep(1/self.log_hz)    

async def main():
    # Initialize
    balloon= Balloon('test')
    # Start Tasks
    tasks = [balloon.get_temp(), balloon.get_gps(), balloon.get_press(), balloon.logcsv()]
    await asyncio.gather(*tasks)
    
    
if __name__=="__main__":
    asyncio.run(main())