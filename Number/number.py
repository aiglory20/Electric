# Edge Impulse - OpenMV Image Classification Example

import sensor
import image
import time
import os
import tf
import uos
import gc

test = False

sensor.reset()
sensor.set_vflip(True)
sensor.set_hmirror(True)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time=2000)
clock = time.clock()

net = None
labels = None
net = tf.load("trained.tflite", load_to_fb=uos.stat(
    'trained.tflite')[6] > (gc.mem_free() - (64*1024)))
# labels = [line.rstrip('\n') for line in open("labels.txt")]
labels = ['3', '4', '5', '6']


def find_number(windos_roi: tuple):
    number_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0}
    while (True):
        if test:
            clock.tick()

        img = sensor.snapshot().binary([(0, 31, -22, 10, -12, 28)])
        img = img.erode(1)
        img = img.dilate(1)

        # TODO:用roi可不可以还是分框
        for obj in net.classify(img, min_scale=1.0, scale_mul=0.8, x_overlap=0.5, y_overlap=0.5, roi=windos_roi):
            predictions_list = list(zip(labels, obj.output()))
            large_count, index = 0, 0
            for i in range(len(predictions_list)):
                if predictions_list[i][1] > large_count:
                    large_count = predictions_list[i][1]
                    index = i
            number_count[(int)(predictions_list[index][0])] += 1
            if test:
                print(
                    "*******\nPredictions at [x=%d,y=%d,w=%d,h=%d]" % obj.rect())
                img.draw_rectangle(obj.rect())
                print(predictions_list[index][0])
                for i in range(len(predictions_list)):
                    print("%s = %f" %
                          (predictions_list[i][0], predictions_list[i][1]))
                print(clock.fps(), "fps")

        for i in number_count:
            if number_count[i] == 10:
                return i


if test:
    print(find_number((80, 0, 80, 120)))
