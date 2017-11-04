import datetime


def fun_insert():
    l = []
    for i in range(0, 50000):
        l.insert(i, i)


def fun_append():
    l = []
    for i in range(0, 50000):
        l.append(i)


def fun(f):
    start_time = datetime.datetime.now()
    f()
    end_time = datetime.datetime.now()
    return (end_time - start_time).microseconds


print("append time =", fun(fun_append), "microseconds")
print("inset time =", fun(fun_insert), "microseconds")