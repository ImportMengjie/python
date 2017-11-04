import random


def redbag(total, num):
    res = [0] * num
    for i in range(0, num):
        t = random.randint(0, total)
        t = t if i < num-1 else total
        res[i] = t
        total -= t
    return res


for k in range(0, 10):
    total = random.randint(10, 20)
    num = random.randint(3, 5)
    print("total = %d, num = %d, result =" % (total, num), redbag(total, num))
