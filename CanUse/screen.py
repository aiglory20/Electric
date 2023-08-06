# LCD Example
#
# Note: To run this example you will need a LCD Shield for your OpenMV Cam.
#
# The LCD Shield allows you to view your OpenMV Cam's frame buffer on the go.

import sensor, image
import lcd # ! important

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # or sensor.GRAYSCALE
sensor.set_framesize(sensor.QQVGA) # Special 128x160 framesize for LCD Shield.
lcd.init() # ! important
#lcd初始化

while(True):
    img = sensor.snapshot().binary([(0,77)])
    img.draw_rectangle((0,0,80,60), color=200)
    img.draw_string(80,60,"sssssss",color=200)
    lcd.display(img) # ! important
    #将图像显示在lcd中
