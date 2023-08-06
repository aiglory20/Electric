""" 送药小车成功"""
import sensor
import image
import time
import math

import os
import tf
import uos
import gc
from pyb import LED, UART

number_print, cross_print = False, False

uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)

LED(1).on()
LED(2).on()
LED(3).on()

THRESHOLD = [(21, 56, 72, 18, 93, -61)]
GRAYSCALE_THRESHOLD = [(0, 77)]

sensor.reset()
sensor.set_vflip(True)
sensor.set_hmirror(True)
sensor.set_framesize(sensor.QQVGA)
sensor.set_pixformat(sensor.RGB565)
sensor.skip_frames(time=1000)
# sensor.set_auto_gain(False) # 颜色跟踪必须关闭自动增益
# sensor.set_auto_whitebal(False) # 颜色跟踪必须关闭白平衡
clock = time.clock()

rois = [
    (50, 100, 60, 20),
    (50, 80, 60, 20),
    (50, 60, 60, 20),
    (50, 40, 60, 20),
    (50, 000, 60, 40),
    (120, 20, 20, 20),  # cross
    (20, 20, 20, 20)  # cross
]


def sending_data(turn_flag, distance, angle, number, sleep_ms):
    global uart
    FH = bytearray([0x2C, 0x12, 66, 66, 66, 66, 0x5B])
    uart.write(FH)
    data = bytearray([0x2C, 0x12, turn_flag,
                     distance, angle, number, 0x5B])
    uart.write(data)
    if sleep_ms > 0:
        time.sleep_ms(sleep_ms)


# 计算最小二乘法直线拟合的参数
def line(points):
    n = len(points)
    sum_x = sum([point[0] for point in points])
    sum_y = sum([point[1] for point in points])
    sum_xy = sum([point[0] * point[1] for point in points])
    sum_x_squared = sum([point[0] ** 2 for point in points])
    m = (n * sum_xy - sum_x * sum_y) / (n * sum_x_squared - sum_x ** 2 + 0.01)
    c = (sum_y - m * sum_x) / n
    distance = abs(c) / math.sqrt(1 + m**2)
    angle = math.degrees(math.atan(m))
    turn_flag = 0
    if angle > 0:
        angle = abs(angle - 90)
        turn_flag = 4
    elif angle == 0:
        turn_flag = 4
    else:
        angle = abs(angle + 90)
        turn_flag = 5
    return angle, distance, turn_flag


net = None
labels = None
net = tf.load("trained.tflite", load_to_fb=uos.stat(
    'trained.tflite')[6] > (gc.mem_free() - (64*1024)))
# labels = [line.rstrip('\n') for line in open("labels.txt")]
labels = ['3', '4', '5', '6']  # TODO: 修改label


def find_number(windos_roi: tuple):
    number_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0}
    while (True):
        sending_data(0, 0, 0, 0, 0)
        if number_print:  # ! number_print
            clock.tick()

        img = sensor.snapshot().binary([(0, 31, -22, 10, -12, 28)])
        img = img.erode(1)
        img = img.dilate(1)

        for obj in net.classify(img, min_scale=1.0, scale_mul=0.8, x_overlap=0.5, y_overlap=0.5, roi=windos_roi):
            predictions_list = list(zip(labels, obj.output()))
            large_count, index = 0, 0
            for i in range(len(predictions_list)):
                if predictions_list[i][1] > large_count:
                    large_count = predictions_list[i][1]
                    index = i
            number_count[(int)(predictions_list[index][0])] += 1
            if number_print:  # ! number_print
                print(
                    "*******\nPredictions at [x=%d,y=%d,w=%d,h=%d]" % obj.rect())
                img.draw_rectangle(obj.rect())
                print(predictions_list[index][0])
                for i in range(len(predictions_list)):
                    print("%s = %f" %
                          (predictions_list[i][0], predictions_list[i][1]))
                print(clock.fps(), "fps")

        # TODO: 是否加一个白板用来第一次识别数字，直到识别到才启动
        for i in number_count:
            if number_count[i] == 20:
                return i


# number = 7
number = find_number((80, 0, 80, 120))
sending_data(66, 66, 99, number, 0)


crosscount = 0  # 十字路口计数
while (True):
    clock.tick()
    img = sensor.snapshot()
    if cross_print:  # ! cross_print
        for i in rois:
            img.draw_rectangle(i, color=200)

    cross_blobs = []
    points = []
    for r in rois:
        blobs = img.find_blobs(THRESHOLD, roi=r[0:4], merge=True)

        if blobs:
            most_pixels = 0
            largest_blob = 0
            for i in range(len(blobs)):
                # 得到最大的色素块
                if blobs[i].pixels() > most_pixels:
                    most_pixels = blobs[i].pixels()
                    largest_blob = i

            # 画出
            if cross_print:  # ! cross_print
                img.draw_rectangle(blobs[largest_blob].rect())
            if (blobs[largest_blob].cx() < 40 or blobs[largest_blob].cx() > 120) and blobs[largest_blob].w() > 10:
                cross_blobs.append((blobs[largest_blob].cx(),
                                    blobs[largest_blob].cy()))
            else:
                points.append((blobs[largest_blob].cx(),
                               blobs[largest_blob].cy()))

    # 0 停止；1 左转；2 右转；3 180度转；4 左微调；5 右微调；6 直走
    turn_flag = {"stop": 0, "90left": 1, "90right": 2, "180": 3,
                 "left": 4, "right": 5, "go": 6}
    if len(cross_blobs) == 2:
        crosscount += 1
        print("crosscount : ", crosscount)
        if crosscount == 1:
            sending_data(turn_flag["go"], 0, 0, crosscount, 550)
            if number == 2:
                sending_data(turn_flag["90left"], 0, 0, crosscount, 0)
            elif number == 1:
                sending_data(turn_flag["90right"], 0, 0, crosscount, 0)
        elif crosscount == 3:
            sending_data(turn_flag['go'], 0, 0, 0, 550)
            sending_data(turn_flag['90left'], 0, 0, 0, 0)
        elif (crosscount == 2 and (number == 3 or number == 4)) or crosscount == 4 or crosscount == 5:

            if number_print:  # ! number_print
                left_number = find_number((0, 0, 80, 120))
                right_number = find_number((80, 0, 80, 120))
                sending_data(66, 66, 99, left_number, 0)
                sending_data(66, 66, 99, right_number, 0)

            if number == find_number((80, 0, 80, 120)):
                t = "90right"
            elif number == find_number((0, 0, 80, 120)):
                t = "90left"
            else:
                t = "180"
            sending_data(turn_flag["go"], 0, 0, 0, 550)
            sending_data(turn_flag[t], 0, 0, 0, 0)
        else:
            sending_data(turn_flag['go'], 0, 0, 0, 550)
    elif len(points) > 4:
        angle, distance, turn_flag = line(points)
        sending_data(turn_flag, (int)(distance / 2.0),
                     (int)(angle), 0, crosscount)
        if cross_print:  # ! cross_print
            print("截距 c:", distance / 2.0, "jiao:", angle, "旋转：",
                  turn_flag, "number:", number)
    elif len(points) < 2:  # 停止
        # 或者再计数前进一会再停止
        sending_data(turn_flag['stop'],
                     0, 0, 0, 0)
    else:
        a = 0
        # TODO :

    # print(clock.fps())
