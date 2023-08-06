"第一版，绿追红激光，pid可以更优化"
import sensor
import image
import time

from pid import PID
from pyb import Servo

start, is_pid, is_print, draw_print = False, True, False, True

yaw_servo = Servo(1)
pitch_servo = Servo(2)
yaw_servo.calibration(500, 2500, 500)
pitch_servo.calibration(500, 2500, 500)


if is_pid:  # ! is_pid
    pan_pid = PID(p=0.023, i=0, imax=90)  # 在线调试使用这个PID
    tilt_pid = PID(p=0.023, i=0, imax=90)  # 在线调试使用这个PID


sensor.reset()  # Initialize the camera sensor.
sensor.set_vflip(True)
sensor.set_hmirror(True)
sensor.set_pixformat(sensor.RGB565)  # use RGB565.
sensor.set_framesize(sensor.VGA)  # use QQVGA for speed.
sensor.skip_frames(time=3000)  # Let new settings take affect.
sensor.set_auto_whitebal(False)  # turn this off.
sensor.set_auto_exposure(False, 30000)
sensor.set_auto_gain(False)  # must be turned off for color tracking
clock = time.clock()  # Tracks FPS.


def find_max(blobs):
    max_size = 0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob = blob
            max_size = blob[2]*blob[3]
    return max_blob


red_threshold = (1, 100, 22, 127, -82, 118)
yaw = 100  # you + zuo -
pitch = 140  # shang + xia -
while (True):
    if start:  # ! start
        yaw_servo.angle(yaw)
        pitch_servo.angle(pitch)
        print(yaw)
        a = 0

    clock.tick()
    img = sensor.snapshot()

    center_x = img.width()/2 + 25
    center_y = img.height()/2 - 156
    img.draw_circle((int)(center_x), (int)
                    (center_y), 2, thickness=2, fill=True)

    blobs = img.find_blobs([red_threshold], roi=(189, 0, 361, 265))
    if blobs:
        max_blob = find_max(blobs)
        x_error = max_blob.cx()-center_x
        y_error = max_blob.cy()-center_y

        if is_print:  # ! is_print
            print(f'x_error:  {x_error},y_error: {y_error}')

        if draw_print:  # ! draw_print
            img.draw_rectangle(max_blob.rect())  # rect
            img.draw_cross(max_blob.cx(), max_blob.cy())  # cx, cy

        if is_pid:  # ! is_pid
            x_output = pan_pid.get_pid(x_error, 0.8)/2
            y_output = tilt_pid.get_pid(y_error, 0.8)
            print("x_output", x_output, "y_output", y_output)

        if is_print:  # ! is_print
            print("yaw : ", yaw, yaw_servo.angle(),
                  "pitch : ",  pitch, pitch_servo.angle())
        # if (abs(x_error) < img.width() * 0.01 and abs(y_error) < img.height() * 0.01):
            # yaw_servo.angle(yaw)
            # pitch_servo.angle(pitch)
        # else:
            # yaw = yaw - x_error / 50.0
            # pitch = pitch - y_error / 50.0
        yaw = yaw - x_output
        pitch = pitch - y_output
        yaw_servo.angle(yaw)
        pitch_servo.angle(pitch)
    else:
        yaw_servo.angle(yaw)
        pitch_servo.angle(pitch)
