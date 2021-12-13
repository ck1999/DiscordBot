class AFor():

    def __init__(self, start, end, step) -> None:
        self.start = start
        self.end = end
        self.step = step

    def __aiter__(self):
        return self

    async def __anext__(self):
        i = self.start
        if i >= self.end:
            raise StopAsyncIteration
        self.start += self.step
        return i

class AFor_Iter():

    def __init__(self, iter: list) -> None:
        self.iter = iter
        self.i = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if len(self.iter) == 0:
            raise StopAsyncIteration
        return self.iter.pop(0)