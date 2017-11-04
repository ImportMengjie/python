class Set:
    def __init__(self, alist: list):
        '''
         alist = alist.copy()
         alist.sort()
         k = 0
         for i in range(0, len(alist) - 1):
             if alist[k] == alist[k + 1]:
                 alist.pop(k)
             else:
                 k = k + 1
         print(alist)
         :param alist: 
        '''
        self.__ilist = []
        for i in alist:
            if i not in self.__ilist:
                self.__ilist.append(i)

    def addElement(self, x):
        if x not in self.__ilist:
            self.__ilist.append(x)

    def deleteElement(self, x):
        if x in self.__ilist:
            self.__ilist.remove(x)

    def isMember(self, x):
        return x in self.__ilist

    def intersection(self, x):
        rtlist = []
        if isinstance(x, (Set,)):
            for i in self.__ilist:
                if i in x.__ilist:
                    rtlist.append(i)
        return rtlist

    def union(self, x):
        rtlist = self.__ilist.copy()
        if isinstance(x, (Set,)):
            for i in x.__ilist:
                if i not in rtlist:
                    rtlist.append(i)
        return rtlist

    def substract(self, x):
        rtlist = []
        if isinstance(x, (Set,)):
            for i in self.__ilist:
                if i not in x.__ilist:
                    rtlist.append(i)
        return rtlist

    def printAll(self):
        print(self.__ilist)


alist = [0, 0, 1, 2, 3, 3, 4, 4, 5, 6, 6, 's', 's']
ilist = [0, 1, 'b', 's', 'c']
s1 = Set(alist)
s2 = Set(ilist)
print("s1")
s1.printAll()
print("s2")
s2.printAll()
print("0 is in s1")
print(s1.isMember(0))
print("-1 is in s1?")
print(s1.isMember(-1))
print("s1 ∩ s2")
print(s1.intersection(s2))
print("s1-s2")
print(s1.substract(s2))
print("s1∪s2")
print(s1.union(s2))
print("s1 addElement b")
s1.addElement('b')
s1.printAll()
print("s1 deleteElement 0")
s1.deleteElement(0)
s1.printAll()
