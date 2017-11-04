import random


def fun(x):
    x = str(x)
    l = []
    for t in x:
        l.append(int(t))
    l.sort()
    min = int("".join(str(i) for i in l))
    l.reverse()
    max = int("".join(str(i) for i in l))
    result = max - min
    if result == int(x):
        return result
    else:
        return fun(result)


for i in range(0, 4):
    x = random.randint(1000, 9999)
    print(fun(x))
