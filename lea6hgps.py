import time
from datetime import datetime
import csv
import asyncio

import serial
import string
from pyubx2 import UBXReader

class BalloonGPS:
    def __init__(self, timeout_sec=2):
        
        self.gpsport = "/dev/ttyS0"
        try:
            ser=serial.Serial(self.gpsport,baudrate=38400,timeout=timeout_sec)
        except:
            print("GPS not connnected")
            
        self.ubr=UBXReader(ser)
        
        self.lat_deg = 0.0
        self.lon_deg = 0.0
        self.heightMSL_m = 0.0
        self.velN_ms = 0.0
        self.velE_ms = 0.0
        self.velD_ms = 0.0
        self.satct = 4
        self.newmsg = 'none'
        return
    
    def gps_update(self, wait=0.2, timeout=2, debug=False):
        posFlag = False
        velFlag = False
        solFlag = False
        starty = time.time()
        finishy = starty + timeout
        while not posFlag or not velFlag or not solFlag:
            start = time.time()
            finish = start + wait
            try:
                (raw,newmsg) = self.ubr.read()
                self.mynewmsg = newmsg
                #print(newmsg)
                if newmsg.identity == 'NAV-POSLLH':
                    self.lat_deg=newmsg.lat
                    self.lon_deg=newmsg.lon
                    self.heightMSL_m=newmsg.hMSL/1000
                    posFlag = True
                        
                elif newmsg.identity == 'NAV-VELNED':
                    self.velN_ms = newmsg.velN/1000
                    self.velE_ms = newmsg.velE/1000
                    self.velD_ms = newmsg.velD/1000
                    velFlag = True
                        
                elif newmsg.identity =='NAV-STATUS':
                    pass  
                elif newmsg.identity =='NAV-SVINFO':
                    pass
                elif newmsg.identity =='NAV-SOL':
                    self.satct = newmsg.numSV
                    solFlag = True
                else:
                    #print('invalid GPS message')
                    pass
            except Exception as e:
                if debug==True:
                    print("GPS Read Error")
                    print(e)
            
            while time.time() < finish:
                pass
            
            if time.time() > finishy:
                break
        return
    
    def gps_test(self, hz=2, duration=10, testdebug=False): 
        for i in range(int(hz*duration)):
            self.gps_update(debug=testdebug)
            print('Longitude (deg): ' +str(self.lat_deg))
            print('Latitude (deg): ' +str(self.lon_deg))
            print('Height MSL (m): ' +str(self.heightMSL_m))
            print('Velocity N (m/s): ' +str(self.velN_ms))
            print('Velocity E (m/s): ' +str(self.velE_ms))
            print('Velocity D (m/s): ' +str(self.velD_ms))
            print('Number of Satellites: ' +str(self.satct))    
            print('\n')
            time.sleep(1/hz)
        print('GPS test complete')
    
    async def gps_asyncwrite_csv(self, logfile, logfileall, reconnect_timeout=20, hz = 2, chunk=20, debug=False):    
        print("GPS Log Starting... ", logfile)
            
        header = ['time',
                  'Longitude (deg)',
                  'Latitude (deg)',
                  'Height MSL (m)',
                  'Velocity N (m/s)',
                  'Velocity E (m/s)',
                  'Velocity D (m/s)',
                  'Number of Satellites'
                  ]

        with open(str(logfile), 'w') as f:
            writer = csv.writer(f)
            writer.writerow(header)
        
        data = [None] * chunk
        dataall = [None] * chunk
        while True:
            for i in range(chunk):
                self.gps_update()
                    
                now = datetime.now()
                times = now.strftime("%H:%M:%S")
                data[i] = [times,
                           self.lon_deg,
                           self.lat_deg,
                           self.heightMSL_m,
                           self.velN_ms,
                           self.velE_ms,
                           self.velD_ms,
                           self.satct]
                
                dataall[i] = str(self.mynewmsg)
                await asyncio.sleep(1/hz)

            with open(logfile, 'a') as f:
                writer = csv.writer(f)
                for i in range(chunk):
                    writer.writerow(data[i])
                if debug == True:
                    print('GPS write')
                    
            with open(logfileall, 'a') as f:
                for line in dataall:
                    f.write(line)
                    f.write('\n')
        return
    
if __name__ == '__main__':
    
    async def main(noasync=False):
        gpsTest = BalloonGPS()
        testfile = '/home/pi/Desktop/HAB/data/data_dump/gps.csv'
        testfileall = '/home/pi/Desktop/HAB/data/data_dump/gpsall.txt'
        
        with open(testfile, 'r+') as f:
            f.truncate(0)
            f.seek(0)
        with open(testfileall, 'r+') as f:
            f.truncate(0)
            f.seek(0)    
        
        #gpsTest.gps_test(duration=5, testdebug=True)
        if noasync == True:
            quit()
        
        task = gpsTest.gps_asyncwrite_csv(testfile, testfileall, chunk=10)
        await asyncio.gather(task)
    
    asyncio.run(main())
    
    
