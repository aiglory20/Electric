# 读取二进制视频示例
#
# 此示例需要使用uSD内存卡
#
# 本示例说明如何使用“图像读取器Image Reader”对象重放由“图像写入器Image Writer”对象保存的OpenMV所看到的图像以测试机器视觉算法。

# 更改为允许从SD卡全速读取，以将序列提取到网络等。
# 将新的暂停参数设置为false

import sensor
import image
import time

snapshot_source = False  # 一旦完成从传感器提取数据，将其设置为true。


sensor.reset()
sensor.set_vflip(True)
sensor.set_hmirror(True)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time=1000)
clock = time.clock()

stream = None
if snapshot_source == False:
    stream = image.ImageIO("/stream.bin", "r")

while (True):
    clock.tick()
    if snapshot_source:
        img = sensor.snapshot()
    else:
        img = stream.read(copy_to_fb=True, loop=True, pause=True)
    # 在此处对图像执行机器视觉算法。
    print(clock.fps())
