import logging
import logging.handlers

from config import settings

def getLogger(arg):
    logger = logging.getLogger(arg)
    logger.setLevel(logging.DEBUG)
    
    filehandler = logging.handlers.TimedRotatingFileHandler(filename=settings.LOGFILE,
                                                        when='midnight',
                                                        interval=1,
                                                        backupCount=7)

    filehandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s')
    filehandler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    #logger.addHandler(filehandler)
    return logger

