""" 基于v2.0将拟合曲线重构为find_blod，但需注意现在是QQVGA，角度没问题，但是偏移量可能得处于2 """
import sensor, image, time, math
from pyb import LED,UART

uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)

LED(1).on()
LED(2).on()
LED(3).on()

THRESHOLD = [(2, 17, 94, -47, 110, -82)]
GRAYSCALE_THRESHOLD = [(0, 77)]

'''
QQQVGA
ROIS = [
        (0, 050, 80, 10, 0.1),
        (0, 040, 80, 10, 0.2),
        (0, 030, 80, 10, 0.2),
        (0, 020, 80, 10, 0.3),
        (0, 000, 80, 20, 0.4)
       ]
'''
ROIS = [
        (0, 100, 160, 20, 0.1),
        (0, 080, 160, 20, 0.2),
        (0, 060, 160, 20, 0.2),
        (0, 040, 160, 20, 0.3),
        (0, 000, 160, 40, 0.4),
       ]
weight_sum = 0 #权值和初始化
for r in ROIS: weight_sum += r[4]

sensor.reset()
sensor.set_vflip(True)
sensor.set_hmirror(True)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)

sensor.skip_frames(30)
#sensor.set_auto_gain(False) # 颜色跟踪必须关闭自动增益
#sensor.set_auto_whitebal(False) # 颜色跟踪必须关闭白平衡
clock = time.clock()

while(True):
    clock.tick()
    most_pixels = 0
    img = sensor.snapshot()
    #centroid_sum = 0
    points = []

    for r in ROIS:
        blobs = img.find_blobs(THRESHOLD, roi=r[0:4], merge=True)

        if blobs:
            largest_blob = 0
            for i in range(len(blobs)):
                #得到最大的色素块
                if blobs[i].pixels() > most_pixels:
                    most_pixels = blobs[i].pixels()
                    largest_blob = i

            #画出
            img.draw_rectangle(blobs[largest_blob].rect())
            points.append((blobs[largest_blob].cx(),
                           blobs[largest_blob].cy()))

            #centroid_sum += blobs[largest_blob].cx() * r[4] #加权点的x

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
            angle = abs(angle -90)
            turn_flag = 0
        else:
            angle = abs(angle + 90)
            turn_flag = 1
        return angle,distance,turn_flag

    angle,distance,turn_flag = line(points)
    FH = bytearray([0x2C, 0x12, (int)(distance), (int)(angle), turn_flag, 1, 0x5B])
    uart.write(FH)

    """ print("截距 c:", distance,"jiao:", angle,"旋转：",turn_flag)
    print(clock.fps()) """

