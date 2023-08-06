""" 云台与镜头固定，然后追随矩形的四个点 """

import sensor
import image
import time
import math
from pyb import Servo
from rect import w_h, sort_points

clock_print, draw_rect, is_print = False, True, False

sensor.reset()
sensor.set_vflip(True)
sensor.set_hmirror(True)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=3000)
sensor.set_auto_exposure(False, 80000)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
clock = time.clock()

yaw_servo = Servo(1)
pitch_servo = Servo(2)
yaw_servo.calibration(500, 2500, 500)
pitch_servo.calibration(500, 2500, 500)


def find_an(corners, w, yaw, pitch):
    k = 0.18 / w  # 0.297
    for i in range(12):
        # img.draw_circle(corners[i][0], corners[i][1], 5, color=(0, 255, 0))
        t_x, t_y = corners[i % 4][0], corners[i % 4][1]
        real_x = (corners[(i+1) % 4][0] - t_x) * k
        real_y = (corners[(i+1) % 4][1] - t_y) * k
        yaw_error = math.degrees(math.atan(real_x))
        pitch_error = math.degrees(math.atan(real_y))
        t_yaw, t_pitch = 0, 0
        max_yaw = abs(yaw_error) + 0.1
        max_pitch = abs(pitch_error) + 0.1
        one_yaw, one_pitch = yaw_error / 200.0, pitch_error / 200.0
        tag = {True: 1, False: -1}
        print(
            f'第{i}个点 , yaw_error : {yaw_error}, pitch_error : {pitch_error}初始 yaw ={yaw} , pitch = {pitch}')
        for j in range(200):
            t_yaw = one_yaw * (j+1)
            t_pitch = one_pitch * (j+1)
            yaw_servo.angle(yaw - t_yaw)
            pitch_servo.angle(pitch - t_pitch)
            time.sleep_ms(8)
        yaw = yaw - t_yaw
        pitch = pitch-t_pitch
        yaw_servo.angle(yaw)
        pitch_servo.angle(pitch)
        print(f'结束的 yaw : {yaw} , pitch : {pitch}')


def find_angle(corners, w, yaw, pitch):
    k = 0.18 / w  # 0.297
    for i in range(4):
        # img.draw_circle(corners[i][0], corners[i][1], 5, color=(0, 255, 0))
        t_x, t_y = corners[i][0], corners[i][1]
        real_x = (corners[(i+1) % 4][0] - t_x) * k
        real_y = (corners[(i+1) % 4][1] - t_y) * k
        yaw_error = math.degrees(math.atan(real_x))
        pitch_error = math.degrees(math.atan(real_y))
        t_yaw, t_pitch = 0, 0
        max_yaw = abs(yaw_error) + 0.1
        max_pitch = abs(pitch_error) + 0.1
        tag = {True: 1, False: -1}
        """ print(
            f'第{i}个点 , yaw_error : {yaw_error}, pitch_error : {pitch_error}初始 yaw ={yaw} , pitch = {pitch}') """
        if (max_yaw > max_pitch):
            while (True):
                if (-max_yaw < t_yaw < max_yaw and -max_pitch < t_pitch < max_pitch):
                    t_yaw = t_yaw + tag[yaw_error > 0] * 0.05
                    t_pitch = t_pitch + tag[pitch_error > 0] * \
                        abs(pitch_error / yaw_error) * 0.05
                    time.sleep_ms(10)
                    yaw_servo.angle(yaw - t_yaw)
                    pitch_servo.angle(pitch - t_pitch)

                    # print(f'yaw : {yaw+t_yaw}, pitch : {pitch+t_pitch}')
                else:
                    yaw = yaw - t_yaw
                    pitch = pitch - t_pitch
                    print(f'结束的 yaw : {yaw} , pitch : {pitch}')
                    break
        else:
            while (True):
                if (-max_yaw < t_yaw < max_yaw and -max_pitch < t_pitch < max_pitch):
                    t_pitch = t_pitch + tag[pitch_error > 0] * 0.05
                    t_yaw = t_yaw + tag[yaw_error > 0] * \
                        abs(yaw_error / pitch_error) * 0.05
                    time.sleep_ms(10)
                    yaw_servo.angle(yaw - t_yaw)
                    pitch_servo.angle(pitch - t_pitch)

                    # print(f'yaw : {yaw+t_yaw}, pitch : {pitch+t_pitch}')
                else:
                    yaw = yaw - t_yaw
                    pitch = pitch-t_pitch
                    print(f'结束的 yaw : {yaw} , pitch : {pitch}')
                    break


is_in = 0
yaw, pitch = yaw_servo.angle(), pitch_servo.angle()
while (True):
    if clock_print:  # ! clock_print
        clock.tick()  # (10, 68, -128, 127, -128, 127)(0, 68, -33, 4, -128, 72)
    img = sensor.snapshot().binary([(0, 70, -128, 127, -128, 127)])
    # img.lens_corr(1.8)
    center_X = (img.width()/2 + 25)
    center_Y = (img.height()/2)
    img.draw_circle((int)(center_X),
                    (int)(center_Y), 2, color=(0, 0, 255), thickness=2, fill=True)

    for r in img.find_rects(threshold=10000):
        corners = sort_points(r.corners())
        w, h = w_h(corners)
        if (1.3 < w/h and w/h < 2):
            # print(f"w = {w} , h = {h}")
            if (2500 < w*h and w*h < 4500):
                if draw_rect:  # ! draw_rect
                    # img.draw_rectangle(r.rect(), color=(255, 0, 0))
                    t = 0
                    for p in corners:
                        img.draw_circle(p[0], p[1], 5, color=(0, 255, 0))
                        img.draw_string(p[0], p[1], (str)(
                            t), color=(0, 255, 0), scale=3)
                        t += 1

                x_error = corners[0][0]-center_X
                y_error = corners[0][1]-center_Y

                if is_print:  # ! is_print
                    print(f'x_error:  {x_error},y_error: {y_error}')

                if draw_rect:  # ! draw_rect
                    '''img.draw_circle(
                        corners[0][0], corners[0][1], 5, color=(0, 0, 255), thickness=2, fill=True)'''

                if is_print:  # ! is_print
                    print("yaw : ", yaw, yaw_servo.angle(),
                          "pitch : ",  pitch, pitch_servo.angle())

                if (abs(x_error) < img.width() * 0.01 and abs(y_error) < img.height() * 0.01):
                    is_in += 1
                    if (is_in > 4):
                        # find_an(corners, w, yaw, pitch)
                        is_in = 0
                else:
                    yaw = yaw - x_error / 20.0
                    pitch = pitch - y_error / 20.0
                    yaw_servo.angle(yaw)
                    pitch_servo.angle(pitch)
        else:
            # pitch = pitch + 1
            yaw_servo.angle(yaw)
            pitch_servo.angle(pitch)
    if clock_print:  # ! clock_print
        print(clock.fps())
