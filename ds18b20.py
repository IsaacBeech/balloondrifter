import time
from datetime import datetime
import csv
import asyncio
import numpy

from w1thermsensor import W1ThermSensor


class BalloonDS18B20:
    def __init__(self, nostop=True):
        init=True
        while True:
            try:
                self.sensor = W1ThermSensor()
            except Exception as e:
                init = False
                print(e)
                print('DS18B20 connection failed, trying again...')
                time.sleep(1)
            if init == True or nostop==True:
                break
        self.temperature_c = 0.0
        
        return
    
    def ds18_update(self, debug=False):
        try:
            self.temperature_c = self.sensor.get_temperature()
        except Exception as e:
            self.temperature_c = 200
            if debug == True:
                print(e)
        return
    
    def ds18_test(self, hz=1, duration =5, testdebug=False): 
        for i in range(int(hz*duration)):
            self.ds18_update(debug=testdebug)
            print('Temperature (C): ' +str(self.temperature_c))
            print('\n')
            time.sleep(1/hz)
            
        print('DS18B20 test complete')
    
    async def ds18_asyncwrite_csv(self, logfile, per = 1, chunk = 20, debug=False):    
        print("Temperature Sensor Log Starting... ", logfile)
        header = ['time',
                  'Temperature (C)'
                  ]

        with open(str(logfile), 'w') as f:
            writer = csv.writer(f)
            writer.writerow(header)
        
        data = [None] * chunk
        while True:
            for i in range(chunk):
                self.ds18_update()
                now = datetime.now()
                times = now.strftime("%H:%M:%S")
                data[i] = [times, self.temperature_c]
                await asyncio.sleep(per)
            with open(logfile, 'a') as f:
                writer = csv.writer(f)
                for i in range(chunk):
                    writer.writerow(data[i])
                if debug == True:
                    print('wrote temp')
            
        
        return
    
if __name__ == '__main__':
    
    async def main():
        ds18Test = BalloonDS18B20()
        testfile = '/home/pi/Desktop/HAB/data/data_dump/ds18b20.csv'
        
        with open(testfile, 'r+') as f:
            f.truncate(0)
            f.seek(0)
        
        ds18Test.ds18_test(duration=10)
        
        task = ds18Test.ds18_asyncwrite_csv(testfile, chunk = 5)
        await asyncio.gather(task)
    
    asyncio.run(main())
    
    
