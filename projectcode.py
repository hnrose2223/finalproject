# Hannah Rose, Sara Lim, Chris Manna

import requests
import sys
import time

sys.path.append('../../Software/Python/')
sys.path.append('../../Software/Python/grove_rgb_lcd')
sys.path.append('/home/pi/Dexter/GrovePi/Software/Python')

#import grovepi
import grove_rgb_lcd as lcd

lcd.setRGB(0, 128, 0)



from ShazamAPI import Shazam
while True:
    try:

        # Display text
        lcd.setText_norefresh('test')

        # Scroll output
       # lcd.setText_norefresh('\n' + CACHE[app][ind:ind+LCD_LINE_LEN])

    except KeyboardInterrupt:
        # Gracefully shutdown on Ctrl-C
        lcd.setText('')
        lcd.setRGB(0, 0, 0)
        
        break

    except IOError as ioe:
        if str(ioe) == '121':
            # Retry after LCD error
            time.sleep(0.25)

        else:
            raise
