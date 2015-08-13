from bitcoincrawler.components.exceptions import CrawlerException


class VoutDecoderException(CrawlerException):
    def __init__(self, msg, method, params):
        super(VoutDecoderException, self).__init__(msg, method, params)