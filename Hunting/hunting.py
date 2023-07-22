""" 基于b站"二筒rrr"的“记录一下openmv+stm32巡线” """

import time
import image
import sensor
from pyb import UART
from pyb import LED
THRESHOLD = (2, 17, 94, -47, 110, -82)


LED(1).on()
LED(2).on()
LED(3).on()

uart = UART(3, 115200, bits=8, parity=None, stop=1)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQQVGA)
sensor.set_vflip(True)
sensor.set_hmirror(True)
sensor.skip_frames(time=2000)
clock = time.clock()


def sending_data(cx, cy, cw, ch):
    global uart
    data = bytearray([0x2C, 0x12, cx, cy, cw, ch, 0x5B])
    # print(cx,cy)
    uart.write(data)


while (True):
    clock.tick()
    img = sensor.snapshot().binary([THRESHOLD])
    cw = 0  # 左转还是右转
    line = img.get_regression([(100, 100)], robust=True)
    if (line):
        rho_err = abs(line.rho())  # 偏移量
        theta_err = line.theta()
        img.draw_line(line.line(), color=127)
        rho_err_temp = abs(line.rho())-img.width()/2

        if line.theta() > 90:
            theta_err_temp = abs(line.theta()-180)
        else:
            theta_err_temp = line.theta()
            cw = 1
        if line.magnitude() > 8:
            sending_data((int)(rho_err), (int)(theta_err_temp), cw, 1)
            # print(rho_err, theta_err)
            # print(rho_err, theta_err_temp,cw)
        pass
