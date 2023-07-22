""" 送药小车 未成功"""
import sensor
import image
import time
import math
from pyb import LED, UART

uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)

LED(1).on()
LED(2).on()
LED(3).on()

# TODO： 红线
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


def sending_data(turn_flag, distance, angle, number):
    global uart
    data = bytearray([0x2C, 0x12, turn_flag,
                     distance, angle, number, 0x5B])
    uart.write(data)


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

# TODO: 上面是不是转弯弄反了
# TODO：第一次数字识别


crosscount = 0  # 十字路口计数
while (True):
    clock.tick()
    img = sensor.snapshot()
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
            img.draw_rectangle(blobs[largest_blob].rect())
            if (blobs[largest_blob].cx() < 40 or blobs[largest_blob].cx() > 120) and blobs[largest_blob].w() > 10:
                cross_blobs.append((blobs[largest_blob].cx(),
                                    blobs[largest_blob].cy()))
            else:
                points.append((blobs[largest_blob].cx(),
                               blobs[largest_blob].cy()))

    turn_flag = 6  # 0 停止；1 左转；2 右转；3 180度转；4 左微调；5 右微调；6 直走
    number = 0
    if len(cross_blobs) == 2:
        crosscount += 1
        # print("crosscount : ", crosscount)
        if crosscount == 1:  # 并且number == 1 or number == 2
            # 暂时是暂停，然后直走，然后左转
            turn_flag = 1
            sending_data(turn_flag, 0, 0, number)
            time.sleep_ms(10000)
            turn_flag = 6
            sending_data(turn_flag, 0, 0, number)
            time.sleep_ms(4000)
            turn_flag = 1
            sending_data(turn_flag, 0, 0, number)
            time.sleep_ms(40000)

        elif crosscount == 2 or crosscount == 4 or crosscount == 5:
            # 暂停识别
            turn_flag = 0
            sending_data(turn_flag, 0, 0, number)
            # TODO : 数字识别,当识别到才跳出
            time.sleep_ms(2000)  # 暂时
            # 计数前进
            turn_flag = 6
            sending_data(turn_flag, 0, 0, number)
            time.sleep_ms(1000)
# 测试用
            if crosscount == 4:
                turn_flag = 1
                sending_data(turn_flag, 0, 0, number)
            """ # TODO： 数字在哪边，进而判断走转还是右转
            turn_flag = 0
            sending_data(turn_flag, 0, 0, number)
            time.sleep_ms(1000)"""
        else:
            # 计数前进
            turn_flag = 6
            sending_data(turn_flag, 0, 0, number)
            time.sleep_ms(1000)
            # 规定默认向左转
            turn_flag = 1
            sending_data(turn_flag, 0, 0, number)
    elif len(points) > 4:
        angle, distance, turn_flag = line(points)
        sending_data(turn_flag, (int)(distance / 2.0),
                     (int)(angle), number)
        print("截距 c:", distance / 2.0, "jiao:", angle, "旋转：",
              turn_flag, "crosscount:", number)
    elif len(points) < 2:  # 停止
        # 或者再计数前进一会再停止
        turn_flag = 0
        sending_data(turn_flag,
                     0, 0, number)
    else:
        a = 0
        # TODO :

    # print(clock.fps())
