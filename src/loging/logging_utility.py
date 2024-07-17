import logging
from src.loging.logger import json_logger
from .schemes import LogMessage,log_en
import datetime

cmd_logger = logging.getLogger(__name__)

def log_info(messege: LogMessage):
    cmd_logger.info(f"INFO: {messege.heder}")

    cmd_logger.info(messege.model_dump_json())

    json_logger.info(messege.model_dump_json())

def log_error(messege: LogMessage):
    cmd_logger.error(f"ERROR: {messege.heder}")

    cmd_logger.error(messege.model_dump_json())

    json_logger.error(messege.model_dump_json())

log_swith = {
    log_en.INFO: log_info,
    log_en.ERROR:log_error
}

def log(messege: LogMessage):
    messege.time = datetime.datetime.now().isoformat()
    log_swith[messege.level](messege)
