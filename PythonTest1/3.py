import operator

def fun(res, loc, L, i):
    """
        res 是结果,loc是L中的位置,i是...
        :rtype: list
    """
    if loc < len(L):
        if res[L[loc][i] - 1] == 0 or res[L[loc][i] - 1] == L[loc][i + 1]:
            res[L[loc][i] - 1] = L[loc][i + 1]
        else:
            return []
        r1 = fun(res.copy(), loc + 1, L, 0)
        r2 = fun(res.copy(), loc + 1, L, 2)
        res = r1 + r2
        i = (0 if i == 2 else 2)
        for r in res.copy():
            if r.count(0) == 1:
                j = r.index(0)
                for k in range(0, len(r) + 1):
                    r[j] = chr(65 + k)
                    if len(set(r)) == len(r):
                        break
            if r[L[loc][i] - 1] == L[loc][i + 1] or len(set(r)) != len(r) or r.count(0) != 0:
                res.remove(r)
        return res
    else:
        return [res]


def getlist():
    r1 = [0] * 5
    r2 = [0] * 5
    A = (2, 'B', 3, 'A')
    B = (2, 'B', 4, 'E')
    C = (1, 'C', 2, 'D')
    D = (5, 'C', 3, 'D')
    E = (4, 'E', 1, 'A')
    L = (A, B, C, D, E)
    res = fun(r1, 0, L, 0) + fun(r2, 0, L, 2)
    for r in res:
        for i in res[res.index(r) + 1:]:
            if operator.eq(r, i):
                res.remove(i)
    return res


print(getlist())
