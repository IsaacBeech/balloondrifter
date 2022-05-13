import time
#time.sleep(10)
import asyncio
import balloon_flight

def main():
    # Initialize
    while True:
        launch_name = input("Name your launch ")
        confirm = input('Are you sure you would like to name your launch "' +launch_name+ '" (y) ')
        if confirm == 'y':
            break
        else:
            pass
    print('\n')
    
    while True:
        floatAlt_ft= input("Set Balloon 1 release altitude (feet MSL): ")
        floatAlt_m = float(floatAlt_ft)*0.3048 # meters
        confirm = input("Are you sure you would like to release Balloon 1 at " +str(floatAlt_ft)+ " ft MSL (" +str(floatAlt_m)+ " meters) (y) ")
        if confirm == 'y':
            break
        else:
            pass
    print('\n')
    
#     while True:
#         floatAltTimeLim= input("Set Balloon 1 release time (minutes): ")
#         confirm = input("Are you sure you would like to release Balloon 1 after " +str(floatAltTimeLim)+ " minutes (y)")
#         if confirm == 'y':
#             break
#         else:
#             pass
#     print('\n')
        
    while True:
        releasetime_min = input("Set minutes before final release: ")
        confirm = input("Are you sure you would like to do a final release after " +str(releasetime_min)+ " minutes (y) ")
        if confirm == 'y':
            break
        else:
            pass
    
    while True:
        record_min = input("Set minutes to record: ")
        confirm = input("Are you sure you would like to record for " +str(record_min)+ " minutes (y) ")
        if confirm == 'y':
            break
        else:
            pass
    
    myballoon = balloon_flight.BalloonFlight(launch_name, floatAlt_m, releasetime_min, record_min)
    asyncio.run(myballoon.main())
    
    
if __name__=="__main__":
    main()
