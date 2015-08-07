from bitcoincrawler.components.exceptions import CrawlerException


class BitcoinCliException(CrawlerException):
    def __init__(self, msg, method, params):
        super(BitcoinCliException, self).__init__(msg, method, params)


class TransactionNotFound(CrawlerException):
    def __init__(self, msg, method, params):
        super(TransactionNotFound, self).__init__(msg, method, params)


class BlockNotFound(CrawlerException):
    def __init__(self, msg, method, params):
        super(BlockNotFound, self).__init__(msg, method, params)