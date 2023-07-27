import time
from pyb import UART, LED
uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)


LED(1).on()
LED(2).on()
LED(3).on()


def sending_data(cx, cy, cw, ch):
    global uart
    data = bytearray([0x2C, 0x12, cx, cy, cw, ch, 0x5B])
    uart.write(data)
    FH = bytearray([0x2C, 0x12, 66, 66, 66, 66, 0x5B])
    uart.write(FH)


i = 0

while (True):
    # 获取个位数
    ones_place = i % 10

    # 获取十位数
    tens_place = (i // 10) % 10

    # 获取百位数
    hundreds_place = i // 100
    cx, cy, cw, ch = ones_place, tens_place, hundreds_place, 0
    sending_data(cx, cy, cw, ch)
    # print(cx, cy, cw, ch)
    i += 1
    time.sleep_ms(300)
