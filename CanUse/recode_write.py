# 写入二进制视频示例
#
# 将此示例与uSD内存卡一起使用！录制后重置相机以查看文件。
#
# 本示例说明如何使用Image Writer对象记录OpenMV Cam所见内容的快照，以供以后使用Image Reader对象进行分析。
# 由Image Writer对象写入磁盘的图像以OpenMV Cam可以读取的简单文件格式存储。

import sensor
import image
import pyb
import time

# ! 特别注意需要改名为main.py
# 只能连接电脑用，插上usb自动运行。
clock_test = True

record_time = 10000  # 10秒（以毫秒为单位）

sensor.reset()
sensor.set_vflip(True)
sensor.set_hmirror(True)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time=1000)
clock = time.clock()

stream = image.ImageIO("/stream.bin", "w")

# 红色LED亮起表示我们正在捕获帧。
pyb.LED(1).on()

start = pyb.millis()
while pyb.elapsed_millis(start) < record_time:
    if clock_test:  # ! clock_test
        clock.tick()
    img = sensor.snapshot()
    # Modify the image if you feel like here...
    stream.write(img)
    if clock_test:  # ! clock_test
        print(clock.fps())

stream.close()

# 蓝色LED亮起表示我们已完成。
pyb.LED(1).off()
pyb.LED(3).on()
