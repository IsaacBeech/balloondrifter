import time
from datetime import datetime
import csv
import asyncio
import board
import adafruit_mpl3115a2

class BalloonMPL:
    def __init__(self, sl_press_pa = 102250):
        #init = True
        #while True:
        try:
            i2c=board.I2C()
            self.sensor = adafruit_mpl3115a2.MPL3115A2(i2c)
            self.sensor.sealevel_pressure = sl_press_pa

        except Exception as e:
            #init=False
            print("Pressure sensor failed to connect)#, trying again... ")
            print(e)
            #time.sleep(1)
#         if init == True:
#             break
            
        self.altitude_m = 0.0
        self.pressure_pa = 0.0
        self.temperature_c = 0.0
        return
    
    def mpl_update(self, debug=False):
        try:
            self.altitude_m = self.sensor.altitude
            self.pressure_pa = self.sensor.pressure
            self.temperature_c = self.sensor.temperature
        except Exception as e:
            self.altitude_m = 100000
            self.pressure_pa = 2000 
            self.temperature_c = 100
            if debug == True:
                print(e)
        return
    
    def mpl_test(self, hz=.5, duration =5, testdebug=False): 
        for i in range(int(hz*duration)):
            self.mpl_update(debug=testdebug)
            print('Altitude (m): ' +str(self.altitude_m))
            print('Pressure (Pa): ' +str(self.pressure_pa))
            print('Temperature (C): ' +str(self.temperature_c))
            print('\n')
            time.sleep(1/hz)
        print('MPL test complete')
    
    async def mpl_asyncwrite_csv(self, logfile, hz = 2, chunk=20, debug=False):    
        print("Pressure Sensor Log Starting... ", logfile)
        header = ['time',
                  'Altitude (m)',
                  'Pressure (Pa)',
                  'Temperature (C)'
                  ]

        with open(str(logfile), 'w') as f:
            writer = csv.writer(f)
            writer.writerow(header)
        
        while True:
            data = [None] * chunk
            while True:
                for i in range(chunk):
                    self.mpl_update()
                    now = datetime.now()
                    times = now.strftime("%H:%M:%S")
                    data[i] = [times,
                               self.altitude_m,
                               self.pressure_pa,
                               self.temperature_c]
                    await asyncio.sleep(1/hz)
                    
                with open(logfile, 'a') as f:
                    writer = csv.writer(f)
                    for i in range(chunk):
                        writer.writerow(data[i])
                    if debug == True:
                        print('press wrote')
        
        return
    
if __name__ == '__main__':
    
    async def main():
        mplTest = BalloonMPL()
        testfile = '/home/pi/Desktop/HAB/data/data_dump/mpl3115.csv'
        
        with open(testfile, 'r+') as f:
            f.truncate(0)
            f.seek(0)
        
        mplTest.mpl_test(duration=2)
        
        task = mplTest.mpl_asyncwrite_csv(testfile, chunk=10)
        await asyncio.gather(task)
    
    asyncio.run(main())
    
    
