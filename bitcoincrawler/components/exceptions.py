class CrawlerException(Exception):
    def __init__(self, msg, method, params):
        Exception(self, msg)
        self.__method = method
        self.__params = params
        self.__msg = msg

    @property
    def method(self):
        return self.__method

    @property
    def params(self):
        return self.__params

    @property
    def msg(self):
        return self.__msg