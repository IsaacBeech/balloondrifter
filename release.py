import time
import RPi.GPIO as GPIO
import pigpio

class BalloonRelease:
    def __init__(self, releasePin1=18, releasePin2=27):
        
        self.openPos1 = 1550
        self.closePos1 = 1300
        self.openPos2 = 1300
        self.closePos2 = 1550
        self.releasePin1 = releasePin1
        self.releasePin2 = releasePin2
        
        self.pwm = pigpio.pi()
        self.pwm.set_mode(self.releasePin1, pigpio.OUTPUT)
        self.pwm.set_PWM_frequency(self.releasePin1, 50)
        self.pwm.set_servo_pulsewidth(self.releasePin1, self.closePos1)
        time.sleep(.25)
        self.pwm.set_servo_pulsewidth(self.releasePin1, 0)
        
        self.pwm.set_mode(self.releasePin2, pigpio.OUTPUT)
        self.pwm.set_PWM_frequency(self.releasePin2, 50)
        self.pwm.set_servo_pulsewidth(self.releasePin2, self.closePos2)
        time.sleep(.25)
        self.pwm.set_servo_pulsewidth(self.releasePin2, 0)
        
        
        return
    
    def open_release1(self):
        self.pwm.set_servo_pulsewidth(self.releasePin1, self.openPos1)
        return
    
    def close_release1(self):
        self.pwm.set_servo_pulsewidth(self.releasePin1, self.closePos1)
        return
    
    def open_release2(self):
        self.pwm.set_servo_pulsewidth(self.releasePin2, self.openPos2)
        return
    
    def close_release2(self):
        self.pwm.set_servo_pulsewidth(self.releasePin2, self.closePos2)
        return
    
    def reverse_release1(self):
        closePos = self.closePos1
        openPos = self.openPos1
        self.closePos1 = openPos
        self.openPos1 = closePos
    
    def reverse_release2(self):
        closePos = self.closePos2
        openPos = self.openPos2
        self.closePos2 = openPos
        self.openPos2 = closePos
    
    def release_preflight(self):
        doublecheck = False
        while not doublecheck:
            while True:
                openclose = input("Release 1: close ('c'), open ('o'), reverse ('r'), or 'done' ")            
                if openclose == 'c':
                    self.close_release1()
                elif openclose =='o':
                    self.open_release1()
                elif openclose =='r':
                    self.reverse_release1()
                elif openclose == 'done':
                    
                    break
                else:
                    print('Invalid input, try again')
            print('\n')
            
            while True:
                openclose = input("Release 2: close ('c'), open ('o'), reverse ('r'), or 'done' ")            
                if openclose == 'c':
                    self.close_release2()
                elif openclose =='o':
                    self.open_release2()
                elif openclose =='r':
                    self.reverse_release2()
                elif openclose == 'done':
                    break
                else:
                    print('Invalid input, try again')
            print('\n')
            
            while True:
                confirm = input("Are you absolutely sure the release mechanisms are closed? ('yes' or 'retry') ")
                if confirm == 'yes':
                    doublecheck = True
                    break
                elif confirm == 'retry':
                    break
                else:
                    print('Invalid input, try again')               
                
        
        
        
if __name__=='__main__':
    releasetest = BalloonRelease()
    releasetest.open_release1()
    releasetest.close_release1()
    releasetest.open_release2()
    releasetest.close_release2()
    releasetest.reverse_release1()
    releasetest.reverse_release2()
    releasetest.release_preflight()
    
