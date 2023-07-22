# Edge Impulse - OpenMV Image Classification Example

import sensor
import image
import time
import os
import tf
import uos
import gc

sensor.reset()                         # Reset and initialize the sensor.
sensor.set_vflip(True)
sensor.set_hmirror(True)
# Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)      # Set frame size to QVGA (320x240)
sensor.set_windowing((80, 0, 80, 120))
# sensor.set_windowing((240, 240))       # Set 240x240 window.
sensor.skip_frames(time=2000)          # Let the camera adjust.

net = None
labels = None

try:
    # load the model, alloc the model file on the heap if we have at least 64K free after loading
    net = tf.load("trained.tflite", load_to_fb=uos.stat(
        'trained.tflite')[6] > (gc.mem_free() - (64*1024)))
except Exception as e:
    print(e)
    raise Exception(
        'Failed to load "trained.tflite", did you copy the .tflite and labels.txt file onto the mass-storage device? (' + str(e) + ')')

try:
    labels = [line.rstrip('\n') for line in open("labels.txt")]
except Exception as e:
    raise Exception(
        'Failed to load "labels.txt", did you copy the .tflite and labels.txt file onto the mass-storage device? (' + str(e) + ')')

clock = time.clock()
while (True):
    clock.tick()

    img = sensor.snapshot().binary([(0, 31, -22, 10, -12, 28)])
    img = img.erode(1)
    img = img.dilate(1)

    # default settings just do one detection... change them to search the image...
    for obj in net.classify(img, min_scale=1.0, scale_mul=0.8, x_overlap=0.5, y_overlap=0.5):
        print("**********\nPredictions at [x=%d,y=%d,w=%d,h=%d]" % obj.rect())
        img.draw_rectangle(obj.rect())
        # This combines the labels and confidence values into a list of tuples
        predictions_list = list(zip(labels, obj.output()))

        ma = 0
        ids = 0
        for i in range(len(predictions_list)):
            if predictions_list[i][1] > ma:
                ma = predictions_list[i][1]
                ids = i

        print("%s = %f" % (predictions_list[ids][0], predictions_list[ids][1]))

        for i in range(len(predictions_list)):
            print("%s = %f" % (predictions_list[i][0], predictions_list[i][1]))

    print(clock.fps(), "fps")
