class Stack:
    def __init__(self):
        self.__stack = []

    def is_empty(self):
        return len(self.__stack) == 0

    def push(self, x):
        self.__stack.append(x)

    def pop(self):
        return None if self.is_empty() else self.__stack.pop()

    def peek(self):
        return None if self.is_empty() else self.__stack[len(self.__stack) - 1]

    def printall(self):
        print(self.__stack)


if '__main__' == __name__:
    s = Stack()
    print(s.is_empty())
    for i in range(0, 10):
        s.push(i)
    s.printall()
    print(s.pop())
    print(s.peek())
    print(s.pop())
    s.printall()
    print(s.is_empty())
