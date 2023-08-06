""" 可用矩形模块 """
import time
import math
import time
test = False


if test:
    import sensor
    import image

if test:
    sensor.reset()
    sensor.set_vflip(True)
    sensor.set_hmirror(True)
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.skip_frames(time=2000)
    sensor.set_auto_exposure(False, 80000)
    sensor.set_auto_gain(False)
    sensor.set_auto_whitebal(False)
    clock = time.clock()


def sort_points(points):
    points = sorted(points, key=lambda x: x[0])
    if points[0][1] < points[1][1]:
        points[0], points[1] = points[1], points[0]
    if points[2][1] > points[3][1]:
        points[2], points[3] = points[3], points[2]
    return points


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
        one_yaw, one_pitch = yaw_error / 200.0, pitch_error / 200.0
        tag = {True: 1, False: -1}
        """ print(
            f'第{i}个点 , yaw_error : {yaw_error}, pitch_error : {pitch_error}初始 yaw ={yaw} , pitch = {pitch}') """
        for i in range(200):
            t_yaw = one_yaw * (i+1)
            t_pitch = one_pitch * (i+1)
            """ time.sleep_ms(10)
                yaw_servo.angle(yaw - t_yaw)
                pitch_servo.angle(pitch - t_pitch) """
        yaw = yaw - t_yaw
        pitch = pitch-t_pitch
        """ print(f'结束的 yaw : {yaw} , pitch : {pitch}') """


def find_an(corners, w, yaw, pitch):
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
        print(
            f'第{i}个点 , yaw_error : {yaw_error}, pitch_error : {pitch_error}初始 yaw ={yaw} , pitch = {pitch}')
        if (max_yaw > max_pitch):
            while (True):
                if (-max_yaw < t_yaw < max_yaw and -max_pitch < t_pitch < max_pitch):
                    t_yaw = t_yaw + tag[yaw_error > 0] * 0.05
                    t_pitch = t_pitch + tag[pitch_error > 0] * \
                        abs(pitch_error / yaw_error) * 0.05
                    """ time.sleep_ms(10)
                    yaw_servo.angle(yaw - t_yaw)
                    pitch_servo.angle(pitch - t_pitch) """

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
                    """ time.sleep_ms(10)
                    yaw_servo.angle(yaw - t_yaw)
                    pitch_servo.angle(pitch - t_pitch) """

                    # print(f'yaw : {yaw+t_yaw}, pitch : {pitch+t_pitch}')
                else:
                    yaw = yaw - t_yaw
                    pitch = pitch-t_pitch
                    print(f'结束的 yaw : {yaw} , pitch : {pitch}')
                    break


def get_points_on_edges(rect_points):
    point_count = 20
    points_on_edges = []
    for i in range(4):
        # 获取当前边的起点和终点
        start_point = rect_points[i]
        end_point = rect_points[(i + 1) % 4]

        # 计算当前边的增量
        dx = (end_point[0] - start_point[0]) / (point_count-1)
        dy = (end_point[1] - start_point[1]) / (point_count-1)

        # 计算当前边上的20个点
        for j in range((point_count)):
            x = start_point[0] + j * dx
            y = start_point[1] + j * dy
            points_on_edges.append((x, y))

    return points_on_edges


def w_h(corners):
    w = math.sqrt((corners[1][0] - corners[0][0])**2 +
                  (corners[1][1] - corners[0][1])**2)
    h = math.sqrt((corners[2][0] - corners[1][0])**2 +
                  (corners[2][1] - corners[1][1])**2)
    if w < h:
        t = w
        w = h
        h = t
    return w, h + 0.1


thresholds = (1, 100, 22, 127, -82, 118)


def test():
    while (True):
        clock.tick()
        img = sensor.snapshot().binary([(0, 68, -33, 4, -128, 72)])

        for r in img.find_rects(threshold=10000):
            corners = sort_points(r.corners())
            w, h = w_h(corners)
            if (1 < w/h and w/h < 2):
                if (2500 < w*h and w*h < 4500):
                    print(corners)
                    '''img.draw_circle(
                        corners[0][0], corners[0][1], 5, color=(0, 0, 255), thickness=3, fill=True)'''

                    points_on_edges = get_points_on_edges(corners)

                    for point in points_on_edges:
                        x, y = point
                        img.draw_circle((int)(x), (int)(y),
                                        2, color=(0, 0, 255))

                    t = 0
                    for p in r.corners():
                        img.draw_circle(p[0], p[1], 5, color=(0, 255, 0))
                        img.draw_string(p[0], p[1], (str)(
                            t), color=(0, 255, 0), scale=3)
                        t += 1
                    # find_angle(r.corners(), w)

        print(clock.fps())


# find_angle([(161, 122), (159, 76), (226, 80), (224, 125)],
        # 67.1193, 82.7997, 167.749)
# find_an([(161, 122), (159, 76), (226, 80), (224, 125)],
        # 67.1193, 82.7997, 167.749)

co = get_points_on_edges([(161, 122), (159, 76), (226, 80), (224, 125)])
print(co)
