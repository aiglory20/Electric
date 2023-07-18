""" 未用到的，和v1.0一个思路，如以后需要分岔路，可以看看 """

import sensor
import image
import time
import math
from pyb import UART, LED

uart = UART(3, 115200)
buf = [0, 0, 0, 0]

round_flag = 0
stop_flag = 0

stop_state = 0
GRAYSCALE_THRESHOLD = [(0, 78)]

ROIS = [  # [ROI, weight]
    (0, 100, 60, 20, 0.6),
    (0,  50, 60, 20, 0.2),
    (0,   0, 60, 20, 0.2),
    (60, 100, 40, 20, 0.6),
    (60,  50, 40, 20, 0.2),
    (60,   0, 40, 20, 0.2)
]

weight_sum = 0

sensor.reset()
sensor.set_vflip(True)
sensor.set_hmirror(True)
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
clock = time.clock()
LED(1).on()
LED(2).on()
LED(3).on()


def uart_recieve():
    global round_flag
    global stop_flag
    global stop_state
    if uart.any():
        rxbuf = uart.read(8)
        # print(rxbuf)
        if len(rxbuf) >= 4:
            for i in range(0, 4):
                if rxbuf[i] == 0xae and i < 4:
                    buf[0] = rxbuf[i]
                    buf[1] = rxbuf[i + 1]
                    buf[2] = rxbuf[i + 2]
                    buf[3] = rxbuf[i + 3]
                    uart.read()
                    # print(buf)
                    # print(clock.fps())
                    round_flag = buf[1]
                    # print(round_flag)
                    stop_flag = buf[2]
                    if stop_flag == 0:
                        stop_state = 0
                    break
    else:
        buf[0] = 0
        buf[1] = 0
        buf[2] = 0
        buf[3] = 0


def uart_send(angle=0, stop=0):
    send_buf = [0xAE, 0, 0, 0, 0, 0xEF]
    angle = angle * 100
    if angle < 0:
        angle = -angle
        send_buf[1] = 1
    if angle < 10:
        send_buf[2] = 0
        send_buf[3] = int(angle)
    elif (angle > 100 and angle < 10000):
        send_buf[2] = int(angle / 100)
        send_buf[3] = int(angle % 100)
    send_buf[4] = stop
    # print(send_buf)
    uart.writechar(send_buf[0])
    uart.writechar(send_buf[1])
    uart.writechar(send_buf[2])
    uart.writechar(send_buf[3])
    uart.writechar(send_buf[4])
    uart.writechar(send_buf[5])


while (True):
    clock.tick()
    # img = sensor.snapshot().lens_corr(strength=1.5, zoom=1.0) # 去除畸变
    img = sensor.snapshot()
    # img.binary(GRAYSCALE_THRESHOLD)

    weight_sum = 0

    centroid_sum = 0
    center_pos = 0
    for r in ROIS:
        blobs = img.find_blobs(GRAYSCALE_THRESHOLD, roi=r[0:4], merge=True)
        weight_sum += r[4]

        if blobs:
            """
            img.draw_rectangle(blobs.rect())
            img.draw_cross(blobs.cx(),blobs.cy())
            """
            largest_blob = max(blobs, key=lambda b: b.pixels())

            img.draw_rectangle(largest_blob.rect())
            img.draw_cross(largest_blob.cx(),
                           largest_blob.cy())

            centroid_sum += largest_blob.cx() * r[4]

    center_pos = (centroid_sum / weight_sum)  # Determine center of line.

    deflection_angle = 0
    deflection_angle = -math.atan((center_pos - 80) / 60)
    deflection_angle = math.degrees(deflection_angle)

    is_turn = 0  # 左转还是右转
    if (deflection_angle < 0):
        is_turn = 1

    """ deflection_angle = abs(deflection_angle)
    if deflection_angle < 15:
        deflection_angle *= 1.5
     else:
        deflection_angle *= 0.8 """

    ones_place = int(abs(deflection_angle)) % 10  # 获取个位数
    tens_place = int(abs(deflection_angle) // 10) % 10  # 获取十位数
    FH = bytearray([0x2C, 0x12, ones_place, tens_place, is_turn, 0, 0x5B])
    uart.write(FH)

    """ print("Turn Angle: %f" % deflection_angle)
    print(is_turn)
    print(tens_place,ones_place)
    print(clock.fps()) """
