import logging
from logging.handlers import RotatingFileHandler
from src.settings import settings

def setup_logger_json(name, filename, level=logging.INFO):
    formatter = logging.Formatter('%(message)s')
    handler = RotatingFileHandler(filename,encoding='utf-8') 
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger

json_logger = setup_logger_json("json",settings.LOG_PATH)