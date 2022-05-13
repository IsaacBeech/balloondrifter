import time
import math
import os
from picamera import PiCamera
import asyncio

class BalloonCamera:
    def __init__(self, directory, vidtime_minutes, minutesperfile = 8):
        try:
            self.camera = PiCamera()
            self.camera.resolution = (1920, 1080)
        except Exception as e:
            print("Pi Camera Failed to Connect")
        
        self.wait_seconds = minutesperfile*60
                
        num_file = math.ceil(int(vidtime_minutes)/int(minutesperfile))
        self.file_array = [None] * int(num_file)
        for i in range(num_file):
            file_name = 'video'+str(i+1)+'.h264'
            file_path = os.path.join(directory,file_name)
            self.file_array[i] = file_path
            with open(file_path, 'w'):
                pass
            
        return
    
    async def record_videos(self, fileformat='h264', camquality=20):
        print("Camera Started Recording")
        for i in self.file_array:
            try:
                self.camera.start_recording(i, format=fileformat, quality=camquality)
            except:
                pass
            await asyncio.sleep(self.wait_seconds)
            try:
                self.camera.stop_recording()
            except:
                pass
        print("Camera Stopped Recording")        
        return
        
    def test_camera(self, preview_time=3):
        self.camera.start_preview()
        time.sleep(preview_time)
        self.camera.stop_preview()
        return    
        
        
if __name__ == '__main__':
    async def main(testonly=False):
        flight = 'mytest'
        directory = '/home/pi/Desktop/HAB/data/video_dump/'
        camtest = BalloonCamera(directory, vidtime_minutes=1, minutesperfile=.5)
        camtest.test_camera(preview_time=5)
        task = camtest.record_videos()
        if testonly==True:
            quit()
        await asyncio.gather(task)
    asyncio.run(main())
