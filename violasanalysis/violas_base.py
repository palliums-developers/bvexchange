#!/usr/bin/python3
import operator
import sys, os
import json
sys.path.append("..")
sys.path.append(os.getcwd())
import log
import hashlib
import traceback
import datetime
import sqlalchemy
import setting
import requests
import comm
import comm.error
import comm.result
import comm.values
from comm.result import result, parse_except
from comm.error import error
from db.dbv2b import dbv2b
from violas.violasclient import violasclient, violaswallet, violasserver
from enum import Enum
from db.dbvfilter import dbvfilter

#module name
name="vbase"

COINS = comm.values.COINS
#load logging
logger = log.logger.getLogger(name) 
    
class vbase(object):
    _step = 1000

    class datatype(Enum):
        V2B = 1
        V2L = 2
        UNKOWN = 255

    class trantype(Enum):
        VIOLAS = 1
        UNKOWN = 255

    def __init__(self, rconf, vnodes):
        self.__connect_db(rconf)
        self.__connect_violas(vnodes)

    def __del__(self):
        self._vclient.disconn_node()

    def __connect_db(self, rconf):
        self._dbclient = dbvfilter(rconf.get("host", "127.0.0.1"), rconf.get("port", 6378), rconf.get("db", "violas_filter"), rconf.get("password", None))
        return self._dbclient

    def __connect_violas(self, vnodes):
        self._vclient = violasclient(vnodes) 
        return self._vclient

    def set_step(self, step):
        if step is None or step <= 0:
            return
        self._step = step

    def get_step(self):
        return self._step

    def parse_type(self, data):
        if data is None or len(data) == 0:
            return self.datatype.UNKOWN
        if data.find("v2b") == 0:
            return self.datatype.V2B
        if data.find("v2l") == 0:
            return self.datatype.V2L
        return self.datatype.UNKOWN

    def is_valid_flag(self, flag):
        return self.parse_tran_type(flag) != self.trantype.UNKOWN
        
    def parse_tran_type(self, flag):
        if flag is None or len(flag) == 0:
            return self.trantype.UNKOWN
        if flag == "violas":
            return self.trantype.VIOLAS
        return self.trantype.UNKOWN
        
    def parse_tran(self, transaction):
        try:
            datas = {"flag": self.trantype.UNKOWN, 
                    "type": self.datatype.UNKOWN, 
                    "btc_address": "",
                    "libra_address": "",
                    "vtbc_address": "",
                    "nettype":"",
                    "state":"",
                    "amount":0,
                    "sender":"",
                    "receiver":"",
                    "vtoken":"",
                    "version":0,
                    "tran_id":0,
                    "tran_state":False

                    }

            tran = result(error.SUCCEED, datas = datas)
    
            #check transaction state
            datas["version"] =  transaction.get("version", 0)
            datas["tran_state"] = transaction.get("success", False)
            if not datas["tran_state"]:
               return tran 

            #must has event(data)
            events = transaction.get("events", None)
            if events is None or len(events) == 0:
               return tran
    

            if events is None or len(events) == 0:
               return tran

            event = events[0].get("event", None)
            if event is None or len(event) == 0:
                return tran
    
            
            data = event.get("data", None)
            if data is None or len(data) == 0:
                return tran

            data_dict = json.loads(data)
            if not self.is_valid_flag(data_dict.get("flag", None)):
                return tran
            
            datas["flag"] = self.parse_tran_type(data_dict.get("flag", None))
            datas["type"] = self.parse_type(data_dict.get("type", None))
            datas["btc_address"] = transaction.get("btc_address", None)
            datas["libra_address"] = data_dict.get("libra_address", None)
            datas["vtbc_address"] = data_dict.get("vtbc_address", None)
            datas["nettype"] = data_dict.get("nettype", None)
            datas["state"] = data_dict.get("state", None)
            datas["amount"] = event.get("amount", 0)
            datas["sender"] = event.get("sender", None)
            datas["receiver"] = event.get("receiver", None)
            datas["vtoken"] = event.get("receiver", None)
            datas["tran_id"] = hashlib.sha3_256(f"{datas['sender']}.{datas['receiver']}.{datas['vtoken']}.{datas['version']}".encode("UTF-8").hexdigest())
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

        
