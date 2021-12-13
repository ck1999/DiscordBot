class StandartCache_List():

    def __init__(self, maxsize: int = 128) -> None:
        self.maxsize = maxsize
        self.list = []

    async def append(self, element):
        if len(self.list) >= self.maxsize:
            self.list.pop(0)
        self.list.append(element)
        yield self.list
    
    async def stats(self):
        yield self.list, self.maxsize

# class SmartElement():

#     def __init__(self, obj: object) -> None:
#         self.count = 0
#         self.obj = obj

#     def __repr__(self) -> str:
#         return self.obj, self.count

class SmartCache_List():

    def __init__(self, maxsize: int = 128) -> None:
        self.maxsize = maxsize
        self.list = {}

    async def append(self, key, element):
        # self.list.sort(key = lambda x: x.count)
        if len(self.list) >= self.maxsize:
            self.list.pop(self.list.keys()[0])
        self.list[key] = (element)

    async def get(self, key):
        if key in self.list.keys():
            return self.list.get(key)
        return None

    async def clear(self):
        yield self.list.clear()

    async def stats(self):
        return self.list, self.maxsize