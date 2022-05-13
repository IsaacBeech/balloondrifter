import time
from datetime import datetime
import asyncio
import os

import balloon_camera
import balloon_ds18b20
import balloon_lea6hgps
import balloon_mpl3115a2
import balloon_release

class BalloonFlight:
    def __init__(self,
                 flight_name,
                 hover_altitude_m,
                 final_cutdown_min,
                 recording_min,
                 equivalent_slpress=102250,
                 main_directory= '/home/pi/Desktop/HAB/data/'):
        
        
        self.flight_name = flight_name
        self.hover_altitude_m = hover_altitude_m
        #self.balloon1_cutdown_sec = balloon1_cutdown_minutes*60
        final_cutdown_sec = int(final_cutdown_min) *60
        self.final_cutdown_sec = int(final_cutdown_sec)
        self.recording_min = recording_min
        
        #create files
        mypath = os.path.join(main_directory, flight_name)
        if not os.path.exists(mypath):
            os.mkdir(mypath)
        else:
            i=0
            while True:
                i+=1
                flight_name_new = flight_name+ str(i)
                mypath = os.path.join(main_directory, flight_name_new)
                if not os.path.exists(mypath):
                    os.mkdir(mypath)
                    break
                else:
                    pass
        vidfolder = os.path.join(mypath, 'video')
        os.mkdir(vidfolder)
        
        myfiles = ['flightlog.txt',
                    'temp_ds18b20.csv',
                    'gps_lea6h.csv',
                    'gpsdump.txt',
                    'press_mpl3115a2.csv']
        
        self.file_array = [None] * len(myfiles)
        i=0
        for file in myfiles:
            file_path = os.path.join(mypath,file)
            self.file_array[i] = file_path
            i+=1
            with open(file_path, 'w'):
                pass
                
        self.mycamera = balloon_camera.BalloonCamera(vidfolder, recording_min)
        self.mytemp = balloon_ds18b20.BalloonDS18B20()
        self.mygps = balloon_lea6hgps.BalloonGPS()
        self.mypress = balloon_mpl3115a2.BalloonMPL(sl_press_pa=equivalent_slpress)
        self.myrelease = balloon_release.BalloonRelease()
        
        self.writelog('Initialized')
        return
    
    def writelog(self, message, print_bool= True):
        if print_bool == True:
            print(str(message))
            print('\n')
        else:
            pass
        now = datetime.now()
        times = now.strftime("%H:%M:%S")
        stringout = str(now) + ' - ' +str(message)
        with open(self.file_array[0], 'a') as f:
            f.write(stringout)
            f.write('\n')
    
    def preflight(self):
        self.writelog('Preflight Started')
        while True:
            go = input('Press Enter to test the ds18b20 temperature sensor, or <any> to pass')
            if go == '':
                self.mytemp.ds18_test()
            else:
                break
        while True:
            go = input('Press Enter to test the GPS sensor, or <any> to pass')
            if go == '':
                self.mygps.gps_test()
            else:
                break
        while True:
            go = input('Press Enter to test the mpl3115a2 pressure/altitude sensor, or <any> to pass')
            if go == '':
                self.mypress.mpl_test()
            else:
                break
        self.writelog('Sensor Tests Complete')
        print('Now open and close the servos until they are secure')
        self.myrelease.release_preflight()
        self.writelog('Servos Closed and Ready')
        print('\n')
        print('Cutdown Time (s): ', self.final_cutdown_sec)
        print('Cutdown Alt (m): ', str(self.hover_altitude_m))
        while True:
            go = input('Press Enter to start data')
            if go == '':
                break
            else:
                pass
        return
    
    async def diagnostics(self, per=5, duration_sec=60):
        start = time.time()
        finish= start+duration_sec
        
        while True:
            print("Lat/Lon/hMSL/Sats: ", str(self.mygps.lat_deg)," ",str(self.mygps.lon_deg)," ",str(self.mygps.heightMSL_m)," ", str(self.mygps.satct))
            print("Temp (C): ", self.mytemp.temperature_c)
            print("Altitude (m): ",self.mypress.altitude_m)
            print('\n')
            await asyncio.sleep(per)
            if time.time()>finish:
                self.writelog('Diagnostics done')
                break
            
        return
    
    async def release1(self, search_period_sec=5, moving_average_size=10, forceOpen=False, forceCt=5):
        self.writelog('Release 1: Armed')
        gpsAltArray = [0.0] * moving_average_size
        pressAltArray = [0.0] * moving_average_size
        i=0
        j=0
        while True:
            # moving average
            gpsAltArray[i] = self.mygps.heightMSL_m
            pressAltArray[i] = self.mypress.altitude_m
            movAvgGPS = sum(gpsAltArray) / len(gpsAltArray)
            movAvgPress = sum(pressAltArray) / len(pressAltArray)
            i+=1
            if i == (moving_average_size-1):
                i=0
            else:
                pass
            
            if movAvgGPS > self.hover_altitude_m or movAvgPress > self.hover_altitude_m:
                self.myrelease.open_release1()
                break
            else:
                j+=1
                if j>forceCt and forceOpen == True:
                    break
                else:
                    pass
                await asyncio.sleep(search_period_sec)
            
        self.writelog('Release 1: Released')
        
        return
    
    async def release2(self):
        self.writelog('Release 2: Armed')
        await asyncio.sleep(self.final_cutdown_sec)
        self.myrelease.open_release1()
        self.myrelease.open_release2()
        self.writelog('Release 2: Released')
        return
    
    async def main(self, mydebug = False):
        if mydebug==False:
            self.preflight()
        else:
            pass
        
        tasks = [self.mycamera.record_videos(),
                 self.mytemp.ds18_asyncwrite_csv(self.file_array[1], debug=mydebug),
                 self.mygps.gps_asyncwrite_csv(self.file_array[2], self.file_array[3], debug=mydebug),
                 self.mypress.mpl_asyncwrite_csv(self.file_array[4], debug=mydebug),
                 self.diagnostics(),
                 self.release1(),
                 self.release2()
                 ]
        await asyncio.gather(*tasks)

if __name__=='__main__':
    name = 'test'
    hover_alt_m = 360 
    cutdown_min = 2
    recording_min =2
    
    quicktest = BalloonFlight(name, hover_alt_m, cutdown_min, recording_min)
    asyncio.run(quicktest.main(mydebug=True))
    
    
    
