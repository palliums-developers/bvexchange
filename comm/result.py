#!/usr/bin/python3

import sys
from . import error
sys.path.append("..")
import traceback
import log
import log.logger
name="result"
error = error.error
name="except" 
logger = log.logger.getLogger(name)
class result:
        state = error.SUCCEED
        message = ""
        datas = ""
        
        def __init__(self, state, message = None, datas = None):
            self.state = state 
            self.message = message
            self.datas = datas


def parse_except(e, msg = None, datas = None):
    try:
        e_type = error.EXCEPT
        raise e
    except Exception as e: #at last
        logger.error(msg)
        logger.error(traceback.format_exc(limit=10))
        if msg is None:
            msg = "Exception"
        if datas is None:
            datas = e

    ret = result(e_type, msg, datas)
    return ret


