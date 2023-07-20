""" 自动泊车 """
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

THRESHOLD = [(2, 17, 94, -47, 110, -82)]
GRAYSCALE_THRESHOLD = [(0, 77)]

sensor.reset()
sensor.set_vflip(True)
sensor.set_hmirror(True)
# TODO ：  旋转90度
sensor.set_framesize(sensor.QQVGA)
sensor.set_pixformat(sensor.RGB565)
sensor.skip_frames(time=1000)
# sensor.set_auto_gain(False) # 颜色跟踪必须关闭自动增益
# sensor.set_auto_whitebal(False) # 颜色跟踪必须关闭白平衡
clock = time.clock()

rois = [
    (0, 100, 100, 20),
    (0, 80, 100, 20),
    (0, 60, 100, 20),
    (0, 40, 100, 20),
    (0, 000, 100, 40),
    (120, 40, 20, 20)  # cross
]

while (True):
    clock.tick()
    img = sensor.snapshot().binary(THRESHOLD)  # 两种方法
    img.draw_rectangle(rois[5], color=200)
    most_pixels = 0
    crosscount = 0  # 十字路口计数
    points = []
    for r in rois:
        blobs = img.find_blobs([(100, 100)], roi=r[0:4], merge=True)

        if blobs:
            largest_blob = 0
            for i in range(len(blobs)):
                # 得到最大的色素块
                if blobs[i].pixels() > most_pixels:
                    most_pixels = blobs[i].pixels()
                    largest_blob = i

            # 画出
            img.draw_rectangle(blobs[largest_blob].rect())
            if blobs[largest_blob].cx() > 100 and blobs[largest_blob].h() > 10:
                crosscount += 1
            else:
                points.append((blobs[largest_blob].cx(),
                               blobs[largest_blob].cy()))

    # 计算最小二乘法直线拟合的参数
    def line(points):
        n = len(points)
        sum_x = sum([point[0] for point in points])
        sum_y = sum([point[1] for point in points])
        sum_xy = sum([point[0] * point[1] for point in points])
        sum_x_squared = sum([point[0] ** 2 for point in points])
        m = (n * sum_xy - sum_x * sum_y) / (n * sum_x_squared - sum_x ** 2)
        c = (sum_y - m * sum_x) / n
        distance = abs(c) / math.sqrt(1 + m**2)
        angle = math.degrees(math.atan(m))
        if angle > 0:
            angle = abs(angle - 90)
            turn_flag = 0
        else:
            angle = abs(angle + 90)
            turn_flag = 1
        return angle, distance, turn_flag

    if len(points) > 4:
        angle, distance, turn_flag = line(points)
        FH = bytearray([0x2C, 0x12, (int)(distance),
                        (int)(angle), turn_flag, crosscount, 0x5B])
        uart.write(FH)
        print("截距 c:", distance, "jiao:", angle, "旋转：",
              turn_flag, "crosscount:", crosscount)
    else:
        a = 0
        # TODO :

    print(clock.fps())
