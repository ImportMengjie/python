import codecs


class Queue:
    def __init__(self):
        self.__queue = []

    def enqueue(self, x):
        self.__queue.append(x)

    def dequeue(self):
        return None if len(self.__queue) == 0 else self.__queue.pop(0)

    def printall(self):
        print(self.__queue)

    def putfile(self, filename):
        with codecs.open(filename, 'a+', 'utf-8') as f:
            for i in self.__queue:
                f.write(str(i) + '\n')

    def getfile(self, filename: str):
        with codecs.open(filename, 'r', 'utf-8') as f:
            for line in f.readlines():
                self.enqueue(line.strip())

    def clear(self):
        self.__queue.clear()


if '__main__' == __name__:
    q = Queue()
    filename = '1.txt'
    for i in range(0, 10):
        q.enqueue(str(i))
    q.printall()
    print("denqueue 2 个元素")
    print(q.dequeue())
    print(q.dequeue())
    q.printall()
    print("写入文件")
    q.putfile(filename)
    print("clear queue")
    q.clear()
    q.printall()
    print("读取文件")
    q.getfile(filename)
    q.printall()
    print("清理文件")
    f = open(filename, 'w')
    f.close()
    print('done')
