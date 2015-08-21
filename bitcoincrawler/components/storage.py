__author__ = 'guido'

class MempoolStorage:
    def __init__(self):
        self._storage = []

    def get(self):
        return self._storage

    def set(self, data):
        if isinstance(data, list):
            self._storage = data
        else:
            raise ValueError('only lists allowed')