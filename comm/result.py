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
        print(traceback.format_exc(limit=10))
        if msg is None:
            msg = "Exception"
        if datas is None:
            datas = e
        ret = result(e_type, msg, datas)
        return ret
    except Exception as e: #at last
        ret = result(error.EXCEPT, "", e)
    return ret


