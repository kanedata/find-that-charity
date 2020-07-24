import logging


class ScrapeHandler(logging.StreamHandler):

    def __init__(self, scrape):
        logging.StreamHandler.__init__(self)
        self.scrape = scrape

    def emit(self, record):
        msg = self.format(record)
        self.scrape.log += msg + '\n'
        if record.levelno in (logging.WARNING, logging.ERROR, logging.CRITICAL):
            self.scrape.errors += 1
        self.scrape.save()
