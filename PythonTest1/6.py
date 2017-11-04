import random
import math


def get_oval_area(a, b, times):
    hit = 0
    for i in range(0, times):
        x = random.uniform(-a, a)
        y = random.uniform(-b, b)
        if (x * x) / (a * a) + (y * y) / (b * b) <= 1:
            hit += 1
    return a * b * (hit / times) * 4


print("times = 100")
print(get_oval_area(5, 4, 100))
print("times = 1000")
print(get_oval_area(5, 4, 1000))
print("times = 10000")
print(get_oval_area(5, 4, 10000))
print("times = 100000")
print(get_oval_area(5, 4, 100000))
print("right answer = %f" % (5 * 4 * math.pi))
