import logging

class LoggerWriter():
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.buffer = ''

    def write(self, message):
        if '\n' not in message:
            self.buffer += message
        else:
            parts = message.split('\n')
            if self.buffer:
                s = self.buffer + parts.pop(0)
                self.logger.log(self.level, s)
            self.buffer = parts.pop()
            for part in parts:
                self.logger.log(self.level, part)

    def flush(self):
        # doesn't actually do anything, but might be expected of a file-like
        # object - so optional depending on your situation
        pass

    def close(self):
        # doesn't actually do anything, but might be expected of a file-like
        # object - so optional depending on your situation. You might want
        # to set a flag so that later calls to write raise an exception
        pass


def init_logger(filename=''):
    import sys
    

    logger = logging.getLogger('launcher')
    logger.setLevel(logging.DEBUG)
    handlers=[]

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    handlers.append(ch)
    #logger.addHandler(ch)
    
    if filename:
        fh = logging.FileHandler(filename)
        fh.setLevel(logging.DEBUG)
        handlers.append(fh)
    #        logger.addHandler(fh)

    logging.basicConfig(level=logging.DEBUG, handlers=handlers)
        
    #info_fp = LoggerWriter(logger, logging.INFO)
    #debug_fp = LoggerWriter(logger, logging.DEBUG)
    #print('An INFO message', file=info_fp)
    #print('A DEBUG message', file=debug_fp)

    sys.stdout = LoggerWriter(logger, logging.INFO)
    sys.stderr = LoggerWriter(logger, logging.WARNING)


if __name__ == "__main__":
    init_logger("/tmp/launcher.log")

