from collections import OrderedDict

class Cache:
    def __init__(self, max_size=100):
        self.cache = OrderedDict()
        self.max_size = max_size
    
    def get(self, key):
        return self.cache.get(key)
    
    def set(self, key, value):
        if len(self.cache) >= self.max_size:
            # Remove the first item (oldest) using FIFO
            self.cache.popitem(last=False)
        self.cache[key] = value