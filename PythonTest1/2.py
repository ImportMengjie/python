import random


def fun1():
    l = range(0, 101)
    s = random.sample(l, 20)
    sum = 0
    for t in s:
        if t % 2 == 1 and t % 3 == 0:
            sum += t
    return sum


def fun2():
    l = list(range(0, 101))
    sum = 0
    for t in range(0, 101):
        s = random.randint(0, 100)
        temp = l[t]
        l[t] = l[s]
        l[s] = temp
    for t in l[0:20]:
        if t % 2 == 1 and t % 3 == 0:
            sum += t
    return sum


def fun3():
    l = []
    sum = 0
    for x in range(1, 21):
        l.append(x * random.randint(1, 5))
    for t in l:
        if t % 2 == 1 and t % 3 == 0:
            sum += t
    return sum

print(fun1())
print(fun2())
print(fun3())
