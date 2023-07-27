import time

# 获取当前时间的时间戳
clock = time.clock()
clock.tick()
i = 0
while i < 1000000000:
    i += 1
    # print(i)
    if i == 10000000:  # 大概23.135秒很准，一帧大概是一毫秒
        print(clock.avg())
        clock.tick()
    elif i == 20000000:
        print(clock.avg())
