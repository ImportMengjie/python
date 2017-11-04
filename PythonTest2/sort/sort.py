def BubbleSort(l: tuple):
    isChange = True
    for i in range(0, len(l)):
        if isChange:
            isChange = False
        else:
            break
        for k in range(len(l) - 1, 0, -1):
            if l[k] < l[k - 1]:
                isChange = True
                t = l[k]
                l[k] = l[k - 1]
                l[k - 1] = t
    return l


def _partition(l: tuple, low: int, high: int):
    sign = l[low]
    while low < high:
        while low < high and l[high] >= sign:
            high -= 1
        l[low] = l[high]
        while low < high and l[low] <= sign:
            low += 1
        l[high] = l[low]
    l[low] = sign
    return low


def _qSort(l: tuple, head: int, rear: int):
    if head < rear:
        mid = _partition(l, head, rear)
        _qSort(l, mid + 1, rear)
        _qSort(l, head, mid - 1)


def QuickSort(l: tuple):
    _qSort(l, 0, len(l) - 1)
    return l


class Sort:
    def __init__(self, lists: tuple = None):
        self._sort = QuickSort
        self._lists = lists

    def setSort(self, x):
        self._sort = x

    def sort(self, lists: tuple = None):
        if lists is not None:
            return self._sort(lists)
        elif self._lists is not None:
            return self._sort(self._lists)
        return None


import datetime
import random

if '__main__' == __name__:
    l1 = list(range(0, 1000))
    random.shuffle(l1)
    l2 = l1.copy()
    s1 = Sort(l1)
    s2 = Sort(l2)
    s2.setSort(BubbleSort)
    print("生成无序序列:" + str(l1))
    print("快速排序开始")
    begin = datetime.datetime.now()
    s1.sort()
    end = datetime.datetime.now()
    print("用时:%0.2fns" % (end - begin).microseconds)
    print("快排结果:" + str(l1))

    print("冒泡排序开始")
    begin = datetime.datetime.now()
    s2.sort()
    end = datetime.datetime.now()
    print("用时:%0.2fns" % (end - begin).microseconds)
    print("冒泡结果:" + str(l1))