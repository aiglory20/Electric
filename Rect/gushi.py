import sensor
import image
import time
import math
import ustruct
from rect import w_h, sort_points
from pyb import UART, LED


clock_print, draw_rect, is_print, draw_print = True, True, False, False

uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)
LED(1).on()
LED(2).on()
LED(3).on()

sensor.reset()
sensor.set_vflip(True)
sensor.set_hmirror(True)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=1000)
sensor.set_auto_exposure(False, 80000)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
clock = time.clock()


threshold_index = 0
thresholds = [((59, 0, 24, 118, 5, 50)),  # generic_red_thresholds
              (30, 100, -64, -8, -32, 32),  # generic_green_thresholds
              (0, 30, 0, 64, -128, 0),
              ((78, 100, -3, 37, -9, 26))]  # generic_blue_thresholds


def transmit_data(flag, x1, y1, x2, y2, x3, y3, x4, y4):
    pack_data = ustruct.pack("<bbhhhhhhhhhb",
                             0x2c,
                             0x12,
                             flag,
                             x1, y1, x2, y2, x3, y3, x4, y4,
                             0x5b
                             )
    return pack_data


# 黑色阈值
black_threshold = (0, 43, -22, 7, -11, 9)  # (15, 23, -16, 0, -5, 9)


def find_rect():
    sensor.set_auto_exposure(False, 80000)
    sensor.set_framesize(sensor.QVGA)
    flagrectwrite = 0
    while (True):
        img = sensor.snapshot()
        img.lens_corr(1.9)  # 畸变矫正

        img_binary = img.binary([black_threshold])
        for r in img_binary.find_rects(threshold=9000, roi=(80, 0, 320, 240)):
            corners = sort_points(r.corners())
            w, h = w_h(corners)
            if (1.3 < w/h and w/h < 1.8):
                if (2500 > w*h or w*h > 4500):
                    continue

                if draw_rect:  # ! draw_rect
                    # img.draw_rectangle(r.rect(), color=(255, 0, 0))
                    t = 0
                    for p in corners:
                        img.draw_circle(p[0], p[1], 5, color=(0, 255, 0))
                        img.draw_string(p[0], p[1], (str)(
                            t), color=(0, 255, 0), scale=3)
                        t += 1

                flagrectwrite += 1
                if (flagrectwrite > 3):
                    return corners


obj_x = obj_y = 0


def find_laser():
    clock.tick()
    img = sensor.snapshot()  # .lens_corr(1.8) #畸变矫正
    global obj_x, obj_y
    # TODO: 调roi
    for blob in img.find_blobs([(1, 100, 22, 127, -82, 118)], roi=(223, 236, 322, 221)):
        if blob:
            if (blob.pixels() > 6):
                obj_x = obj_y = 0
                continue
            img.draw_circle(blob.cx(), blob.cy(), 5, color=(
                0, 255, 0), thickness=2, fill=True)
            if obj_x is not None:
                obj_x = blob.cx()
            if obj_y is not None:
                obj_y = blob.cy()
        else:
            obj_x = obj_y = 0
    # for blob in img.find_blobs([thresholds[3]], pixels_threshold=5, area_threshold=5, merge=True, roi=(262,215,233,191)):
        # if blob:
            # if (blob.pixels() > 30):
            # obj_x = obj_y = 0
            # continue

            # img.draw_circle(blob.cx(), blob.cy(),5,color=(0, 255, 0), thickness=2, fill=True)
            # if obj_x is not None:
            # obj_x = blob.cx()
            # if obj_y is not None:
            # obj_y = blob.cy()
        # else:
            # obj_x = obj_y = 0


def color_blob(threshold):
    img = sensor.snapshot()
    blobs = img.find_blobs([threshold], roi=(225, 221, 316, 225))
    if len(blobs) >= 1:
        # Draw a rect around the blob.
        b = blobs[0]
        img.draw_rectangle(b[0:4])  # rect
        cx = b[5]
        cy = b[6]
        img.draw_cross(b[5], b[6])  # cx, cy
        img.draw_circle(b[5], b[6], 5, thickness=2, fill=True)
        return b[5], b[6], img.width(), img.height()
    return 0, 0, 0, 0


is_in, nodo = 0, 0
index = 0
yaw, pitch = 100, 160
corners = find_rect()
# 坐标转换得*2
for i in range(5):
    date = transmit_data(1, corners[0][0] * 2, corners[0][1]*2, corners[1][0]*2,
                         corners[1][1]*2, corners[2][0]*2, corners[2][1]*2, corners[3][0]*2, corners[3][1]*2)
    uart.write(date)
    time.sleep_ms(10)

sensor.set_framesize(sensor.VGA)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
sensor.set_auto_exposure(False, 9000)
is_to = 0
while (True):
    center_X, center_Y = 0, 0  # (6, 100, -128, 127, -128, 127)
    center_X, center_Y, width, height = color_blob((1, 100, 22, 127, -82, 118))

    if (center_X == 0 and center_Y == 0):
        continue

    # print(center_X, center_Y)
    if draw_print:  # ! draw_print
        t = 0
        for p in corners:
            img.draw_circle(p[0], p[1], 5, color=(0, 255, 0))
            img.draw_string(p[0], p[1], (str)(
                t), color=(0, 255, 0), scale=3)
            t += 1
    # print(center_X, center_Y, width, height)
    date = transmit_data(2, center_X, center_Y, width, height, 0, 0, 0, 0)
    uart.write(date)
    time.sleep_ms(100)
    is_to += 1
    print(is_to)
    if (is_to % 250 == 0):
        corners = find_rect()
        # 坐标转换得*2
        for i in range(5):
            date = transmit_data(1, corners[0][0] * 2, corners[0][1]*2, corners[1][0]*2,
                                 corners[1][1]*2, corners[2][0]*2, corners[2][1]*2, corners[3][0]*2, corners[3][1]*2)
            uart.write(date)
            time.sleep_ms(10)
        sensor.set_framesize(sensor.VGA)
        sensor.set_auto_gain(False)
        sensor.set_auto_whitebal(False)
        sensor.set_auto_exposure(False, 10000)
