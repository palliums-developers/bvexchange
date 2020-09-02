#!/usr/bin/python3
import operator
import sys, os
import json
sys.path.append(os.getcwd())
sys.path.append("..")
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import stmanage
import requests
import comm
import comm.error
import comm.result
import comm.values
from comm.result import result, parse_except
from comm.error import error
from db.dblocal import dblocal as localdb
import vlsopt.violasclient
from vlsopt.violasclient import violasclient, violaswallet, violasserver
from vlsopt.violasproof import violasproof
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from baseobject import baseobject
from enum import Enum
from vrequest.request_client import requestclient
from exchange.exbase import exbase

#module self.name
#name="exlv"
wallet_name = "vwallet"

VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN
#load logging
class l2v(exbase):    
    def __init__(self, name, 
            dtype, 
            vlsnodes, 
            lbrnodes, 
            proofdb, 
            receivers, 
            senders, 
            swap_module,
            swap_owner):

        exbase.__init__(self, name, dtype, \
                None, vlsnodes, lbrnodes, \
                proofdb, receivers, senders, \
                swap_module, swap_owner,\
                "libra", "violas")
        self.init_exec_states()

    def __del__(self):
        pass

    def init_exec_states(self):

        self.append_property("use_exec_update_db_states", 
                [localdb.state.VSUCCEED, localdb.state.SSUCCEED])

        self.append_property("use_exec_failed_state", 
            [state for state in localdb.state \
                    if state not in [localdb.state.COMPLETE, \
                        localdb.state.VSUCCEED, \
                        localdb.state.SSUCCEED]])

    def exec_exchange(self, data, from_sender, map_sender, combine_account, receiver, \
            state = None, detail = {}):
        fromaddress = data["address"]
        amount      = int(data["amount"]) 
        sequence    = data["sequence"] 
        version     = data["version"]
        toaddress   = data["to_address"] #map token to
        tran_id     = data["tran_id"]
        out_amount  = int(data["out_amount"])
        times       = data["times"]
        opttype     = data["opttype"]
        stable_token_id = data["token_id"]
        from_token_id = stable_token_id
        map_token_id = stmanage.get_token_map(stable_token_id) #stable token -> LBRXXX token
        to_token_id    = self.to_token_id #token_id is map 

        ret = result(error.FAILED)
        self._logger.info(f"start exchange {self.dtype}. version={version}, state = {state}, detail = {detail} datas from server.")

        if state is not None:
            self.latest_version[receiver] = max(version, self.latest_version.get(receiver, -1))

        #if found transaction in history.db, then get_transactions's latest_version is error(too small or other case)'
        if state is None and self.has_info(tran_id):
            return ret

        if not self.chain_data_is_valid(data):
           return 

        if self.use_module(state, localdb.state.START):
            self.insert_to_localdb_with_check(version, localdb.state.START, tran_id, receiver)

        if self.use_module(state, localdb.state.PSUCCEED) or \
                self.use_module(state, localdb.state.ESUCCEED) or \
                self.use_module(state, localdb.state.FILLSUCCEED):
            #get output and gas
            ret = self.violas_client.swap_get_output_amount(map_token_id, to_token_id, amount)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.FAILED)
                return ret
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.ESUCCEED)

            out_amount_chian, gas = ret.datas
            #temp value(test)
            if out_amount <= 0:
                out_amount = out_amount_chian
            elif out_amount > out_amount_chian: #don't execute swap, Reduce the cost of the budget
                self.update_localdb_state_with_check(tran_id, localdb.state.FAILED)
                return ret
            detail.update({"gas": gas})

            #mint LBRXXX to sender(type = LBRXXX), or check sender's token amount is enough
            ret = self.fill_address_token[self.map_chain](map_sender.address.hex(), map_token_id, amount, detail["gas"])
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.FILLFAILED, \
                      json.dumps(detail))
                return ret
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.FILLSUCCEED, \
                      json.dumps(detail))

            #swap LBRXXX -> VLSYYY and send VLSXXX to toaddress(client payee address)
            detail.update({"diff_balance": out_amount_chian})
            ret = self.violas_client.swap(map_sender, map_token_id, to_token_id, amount, \
                    out_amount, receiver = toaddress, gas_currency_code = map_token_id)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.PFAILED, json.dumps(detail))
                return ret
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.PSUCCEED, json.dumps(detail))
        
        #send libra token to toaddress
        #sendexproofmark succeed , send violas coin with data for change tran state
        if self.use_module(state, localdb.state.VSUCCEED):
            ret =  self.send_coin_for_update_state_to_end(from_sender, receiver, tran_id, from_token_id, 1, out_amount_real=detail.get("diff_balance", 0))
            if ret.state != error.SUCCEED:
                return ret

        return result(error.SUCCEED)

def main():
       print("start main")
       stmanage.set_conf_env("../bvexchange.toml")
       mod = "l2vgbp"
       dtype = "l2vgbp"
       obj = l2v(mod, 
               dtype,
               stmanage.get_violas_nodes(), 
               stmanage.get_libra_nodes(),
               stmanage.get_db(dtype), 
               list(set(stmanage.get_receiver_address_list(dtype, "libra", False))),
               list(set(stmanage.get_sender_address_list(dtype, "violas", False))),
               stmanage.get_swap_module(),
               stmanage.get_swap_owner(),
               )
       ret = obj.start()
       if ret.state != error.SUCCEED:
           print(ret.message)

if __name__ == "__main__":
    main()
