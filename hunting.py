# https://blog.csdn.net/weixin_48267104/article/details/112986168

import sensor, image, time, math
from pyb import LED,UART

uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)

LED(1).on()
LED(2).on()
LED(3).on()

# 跟踪一条黑线。使用[(128,255)]来跟踪白线。
THRESHOLD = [(2, 17, 94, -47, 110, -82)]#[(2, 26, 94, -47, 110, -82)]
GRAYSCALE_THRESHOLD = [(0, 77)]
#设置阈值，如果是黑线，GRAYSCALE_THRESHOLD = [(0, 64)]；
#如果是白线，GRAYSCALE_THRESHOLD = [(128，255)]

ROIS = [
        (0, 100, 160, 20, 0.7),
        (0, 050, 160, 20, 0.3),
        (0, 000, 160, 20, 0.1)
       ]

weight_sum = 0 #权值和初始化
for r in ROIS: weight_sum += r[4]

sensor.reset()
sensor.set_vflip(True) # 这两者是图片翻转，当出现小车向反方向转动可以整整
sensor.set_hmirror(True)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA) # 使用QQVGA的速度。

sensor.skip_frames(30)
#sensor.set_auto_gain(False) # 颜色跟踪必须关闭自动增益
#sensor.set_auto_whitebal(False) # 颜色跟踪必须关闭白平衡
clock = time.clock()

while(True):
    clock.tick()
    most_pixels = 0
    img = sensor.snapshot()
    centroid_sum = 0

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
            img.draw_cross(blobs[largest_blob].cx(),
                           blobs[largest_blob].cy())
            #print(blobs[largest_blob].pixels(),blobs[largest_blob].cw(),blobs[largest_blob].ch())

            centroid_sum += blobs[largest_blob].cx() * r[4] #加权点的x


    center_pos = (centroid_sum / weight_sum) #中间公式
    deflection_angle = 0 #机器人应该转的角度
    deflection_angle = -math.atan((center_pos-80)/60)

    #角度计算.80 60 分别为图像宽和高的一半，图像大小为QQVGA 160x120.
    # 下面的等式只是计算三角形的角度，其中三角形的另一边是中心位置与中心的偏差，相邻边是Y的一半。

    deflection_angle = math.degrees(deflection_angle) * 0.7 #将计算结果的弧度值转化为角度值

    is_turn = 0 # 左转还是右转
    if(deflection_angle<0):
        is_turn = 1

    ones_place = int(abs(deflection_angle)) % 10 # 获取个位数
    tens_place = int(abs(deflection_angle) // 10) % 10 # 获取十位数
    FH = bytearray([0x2C, 0x12, ones_place, tens_place, is_turn, 0, 0x5B])
    uart.write(FH)

    """ print("Turn Angle: %f" % deflection_angle)
    print(is_turn)
    print(tens_place,ones_place)
    print(clock.fps()) """

