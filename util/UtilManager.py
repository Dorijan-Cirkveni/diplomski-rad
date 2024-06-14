import json
from collections import deque

from util.CommonExceptions import ImplementAsNeededException


class Counter:
    def __init__(self, value: float = 0):
        self.value = value - 1

    def use(self):
        self.value += 1
        return self.value

    def __call__(self):
        self.value += 1
        return self.value


class SetQueue:
    def __init__(self):
        self.Q = deque()
        self.S = set()

    def add(self, E):
        if E in self.S:
            return False
        self.Q.append(E)
        self.S.add(E)
        return True

    def clear(self):
        while self.Q:
            if self.Q[-1] in self.S:
                break
            self.Q.pop()
        while self.Q:
            if self.Q[0] in self.S:
                break
            self.Q.popleft()
        return

    def remove(self, E):
        if E not in self.S:
            return False
        self.S.remove(E)
        self.clear()

    def pop(self):
        if not self.Q:
            return
        E = self.Q.pop()
        self.S.remove(E)
        self.clear()
        return

    def popleft(self):
        if not self.Q:
            return
        E = self.Q.popleft()
        self.S.remove(E)
        self.clear()
        return

def IsValidJSON(s):
    try:
        json.loads(s)
        return True
    except json.decoder.JSONDecodeError:
        return False


def MakeClassNameReadable(s: str):
    new = [""]
    for e in s:
        if not new[-1]:
            new[-1] += e.upper()
            continue
        if e.isupper():
            new.append(e)
            continue
        if e == "_":
            new.append("")
            continue
        new[-1] += e
    while not new[-1]:
        new.pop()
    return " ".join(new)


def StringLimbo(s: str, maxspace, splitter=" "):
    L = []
    cur = ""
    SL = s.split(splitter) + ["A" * (maxspace + 1)]
    for e in SL:
        k = len(e)
        if len(cur) + k + 1 > maxspace and cur:
            L.append(cur)
            cur = ""
        if cur:
            cur += " "
        cur += e
    return "\n".join(L)


def ProcessClassName(s: str, maxspace=16, splitter=" "):
    return StringLimbo(MakeClassNameReadable(s), maxspace, splitter)


def DoNothing(*_, **__):
    """
    This function does nothing.
    :param _:
    :param __:
    :return:
    """
    return


def ConfirmQuit(message: str = "Are you sure? [Y/N]", *_, **__):
    command = ""
    while "Y" not in command and "N" not in command:
        command = input(message)
        command = command.upper()
    if "Y" in command:
        exit()
    return


def PrintAndReturn(var):
    print(var)
    return var


def CallOrEqual(condition, value):
    if callable(condition):
        return condition(value)
    else:
        return condition == value


def reverseIf(E, cond):
    return (E[1], E[0]) if cond else E


def limrange(start, end, step, limit):
    if step > 0:
        end = min(end, limit)
    else:
        end = max(end, limit)
    return range(start, end, step)


def AdjustRatio(size, ratio: list):
    s = sum(ratio)
    adjRatio = [e * size / s for e in ratio]
    adjRatio = [(i, int(e), e - int(e)) for i, e in enumerate(adjRatio)]
    adjRatio.sort(key=lambda e: e[2])
    if adjRatio[-1][1] != 0:
        rem = size - sum([e[1] for e in adjRatio])
        temp = []
        for i in range(rem):
            E = adjRatio.pop()
            temp.append((E[0], E[1] + 1))
        temp.extend(adjRatio)
        temp.sort()
        adjRatio = temp
    adjRatio = [e[1] for e in adjRatio]
    return adjRatio


def AddValueToLayeredStruct(S: [dict, list], types: list[type], indices: list, value, mode: str):
    stack = []
    for i, e in enumerate(indices):
        stack.append((S, e))
        if type(S) == list:
            if type(e) != int:
                raise Exception("figure it out yourself")
            if e not in range(len(S)):
                raise Exception("figure it out yourself")
        elif type(S) == dict:
            S = S.get(e, types[i]())
    if mode == "a":
        if type(S) == list:
            S.append(value)
            value = S
    while stack:
        S, e = stack.pop()
        S[e] = value
        value = S
    raise ImplementAsNeededException()


def main():
    s = "Hello World"
    s2 = StringLimbo(s, 10)
    print(s2)
    return


if __name__ == "__main__":
    main()
