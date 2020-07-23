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
from db.dbv2l import dbv2l as localdb
import vlsopt.violasclient
from vlsopt.violasclient import violasclient, violaswallet, violasserver
from vlsopt.violasproof import violasproof
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from baseobject import baseobject
from enum import Enum
from vrequest.request_client import requestclient
from exchange.vbbase import vbbase

#module self.name
#name="exlv"
wallet_name = "vwallet"

VIOLAS_ADDRESS_LEN = comm.values.VIOLAS_ADDRESS_LEN
#load logging
class v2b(vbbase):    
    def __init__(self, 
            name, 
            dtype, 
            vlsnodes, 
            btcnodes, 
            proofdb, 
            receivers, 
            senders, 
            combine, 
            swap_module,
            swap_owner):
        ''' violas stable token swap to bitcoin BTC
            @dtype : opttype
            @vlsnodes: violas nodes configure
            @btcnodes: btc node configure
            @proofdb: violas proof configure
            @receivers: violas receivers address
            @senders: btc address, use this address to transfer
            @combine: violas address, use this address store swap token 
            @swap_module: swap module address
            @swap_owner: swap owner address
        '''
        vbbase.__init__(self, name, dtype, btcnodes, vlsnodes, \
                proofdb, receivers, senders, swap_module, swap_owner,\
                "violas", "btc")
        self.append_property("combine", combine)

        self.init_extend_property()
        self.init_exec_states()

    def __del__(self):
        pass

    def init_extend_property(self):
        ret = self.violas_wallet.get_account(self.combine)
        self.check_state_raise(ret, f"get combine({self.combine})'s account failed.")
        self.append_property("combine_account", ret.datas)

    def init_exec_states(self):

        self.append_property("use_exec_update_db_states", 
                [localdb.state.VSUCCEED, localdb.state.SSUCCEED])

        self.append_property("use_exec_failed_state", 
            [state for state in localdb.state \
                    if state not in [localdb.state.COMPLETE, \
                        localdb.state.VSUCCEED, \
                        localdb.state.SSUCCEED]])

    def fill_address_token(self, address, token_id, amount, gas=40_000):
        try:
            ret = self.btc_client.get_balance(address)
            assert ret.state == error.SUCCEED, f"get balance failed"
            
            cur_amount = ret.datas
            if cur_amount < amount + gas:
                #get some coin for address
                pass

            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def exec_exchange(self, data, from_sender, map_sender, combine_account, receiver, \
            state = None, detail = {}):
        ''' execute exchange 
            @data : proof datas
            @from_sender: 
            @map_sender:
            @combine_account: inner 
            @receiver: swap transaction's server address
            @state: check is new exchange or re-execute exchange with it, 
                    None is new, other is re-execute
            detail: when state is not None , get some info from detail
        '''
        sender      = data["address"]
        amount      = int(data["amount"]) 
        sequence    = data["sequence"] 
        version     = data["version"]
        toaddress   = data["to_address"] #map token to
        tran_id     = data["tran_id"]
        out_amount  = data["out_amount"]
        times       = data["times"]
        opttype     = data["opttype"]
        from_token_id = data["token_id"] #VLSXXX
        to_token_id = self.to_token_id
        map_token_id = stmanage.get_token_map(to_token_id) #stable token -> LBRXXX token
        assert map_token_id is not None, f"get token({to_token_id}) failed, check config token_map"

        self._logger.info(f"exec_exchange-start. start exec_exchange . tran_id={tran_id}, state = {state}.")

        #only violas and violas use this , btc can't use version
        if state is not None:
            self.latest_version[receiver] = max(version, self.latest_version.get(receiver, -1))

        #if found transaction in history.db(state == None), 
        #then get_transactions's latest_version is error(too small or other case)' 
        if state is None and self.has_info(tran_id):
            return ret

        if not self.chain_data_is_valid(data):
            return ret 

        if self.use_module(state, localdb.state.START):
            self.insert_to_localdb_with_check(version, localdb.state.START, tran_id, receiver)
        #get swap before amount(map_token_id)
        
        if self.use_module(state, localdb.state.ESUCCEED):
            ret = self.violas_client.get_balance(combine_account.address.hex(), map_token_id)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.FAILED)
                return ret
            before_amount = ret.datas
            detail.update({"before_amount": before_amount})

            #get gas for swap
            self._logger.debug(f"exec_exchange-1. start swap_get_output_amount({map_token_id} {to_token_id} {amount})...")
            ret = self.violas_client.swap_get_output_amount(from_token_id, map_token_id, amount)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.FAILED)
                return ret 
            out_amount_chian, gas = ret.datas
            self._logger.debug(f"exec_exchange-1.result : out_amount = {out_amount_chian} gas = {gas}")

            #temp value(test)
            if out_amount <= 0:
                out_amount = out_amount_chian
            elif out_amount > out_amount_chian: #don't execute swap, Reduce the cost of the budget
                self.update_localdb_state_with_check(tran_id, localdb.state.FAILED)
                return result(error.FAILED, \
                            f"don't execute swap(out_amount({out_amount}) > cur_outamount({out_amount_chian})), Reduce the cost of the budget")
            detail.update({"gas": gas})

            #swap LBRXXX -> VLSYYY
            self._logger.debug("exec_exchange-2. start swap...")
            ret = self.violas_client.swap(from_sender, from_token_id, map_token_id, amount, \
                    out_amount, receiver = combine_account.address.hex(), \
                    gas_currency_code = from_token_id)

            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.FAILED)
                self._logger.debug("exec_exchange-2.result: failed.")
                return ret
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.SUCCEED)

            #get swap after amount(map_token_id)
            ret = self.violas_client.get_balance(combine_account.address.hex(), map_token_id)
            if ret.state != error.SUCCEED:
                ret = self.violas_client.get_address_version(combine_account.address.hex())
                self.check_state_raise(ret, f"get_address_version({combine_account.address.hex})")
                detail.update({"swap_version": ret.datas})

                #if get balance, next execute, balance will change , so re swap, 
                #but combine token(map_token_id) is change, this time swap token_id should be burn
                self.update_localdb_state_with_check(tran_id, localdb.state.QBFAILED, \
                        json.dumps(detail)) #should get swap to_token balance from version
                return ret
            after_amount = ret.datas

            #clac diff balance
            diff_balance = after_amount - before_amount
            detail.update({"diff_balance": diff_balance})

        #mint LBRXXX to sender(type = LBRXXX), or check sender's token amount is enough, re fill ????
        if self.use_module(state, localdb.state.FILLSUCCEED) or \
                self.use_module(state, localdb.state.PSUCCEED):

            self._logger.debug("exec_exchange-3. start fill_address_token...")
            btc_amount = self.amountswap(detail["diff_balance"]).btc_amount
            ret = self.fill_address_token(map_sender.address.hex(), to_token_id, \
                    btc_amount)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.FILLFAILED, \
                        json.dumps(detail))
                self._logger.debug("exec_exchange-3.result: failed.")
                return ret

        #send btc token to payee address. P = payee
            markdata = self.btc_client.create_data_for_mark(self.btc_chain, self.dtype, \
                    tran_id, version)

            self._logger.debug("exec_exchange-4. start send btc to {toaddress} amount = {btc_amount}...")
            ret = self.btc_client.send_coin(map_sender, toaddress, \
                    btc_amount, to_token_id, data=markdata)
            if ret.state != error.SUCCEED:
                self.update_localdb_state_with_check(tran_id, localdb.state.PFAILED, \
                        json.dumps(detail))
                self._logger.debug("exec_exchange-4.result: failed.")
                return ret
            else:
                self.update_localdb_state_with_check(tran_id, localdb.state.PSUCCEED)

        #send libra token to toaddress
        #sendexproofmark succeed , send violas coin with data for change tran state
        if self.use_module(state, localdb.state.VSUCCEED):
            self._logger.debug("exec_exchange-5. start send_coin_for_update_state_to_end({receiver}, {tran_id})...")
            self.send_coin_for_update_state_to_end(from_sender, receiver, tran_id, \
                    from_token_id, version = version)
        self._logger.debug("exec_exchange-end.")

def main():
       print("start main")
       
       stmanage.set_conf_env("../bvexchange.toml")
       mod = "v2b"
       dtype = "v2b"
       obj = v2b(mod, 
               dtype,
               stmanage.get_violas_nodes(), 
               stmanage.get_btc_nodes(),
               stmanage.get_db(dtype), 
               list(set(stmanage.get_receiver_address_list(dtype, "violas", False))),
               list(set(stmanage.get_sender_address_list(dtype, "btc", False))),
               stmanage.get_combine_address(dtype, "violas"),
               stmanage.get_swap_module(),
               stmanage.get_swap_owner()
               )
       ret = obj.start()
       if ret.state != error.SUCCEED:
           print(ret.message)

if __name__ == "__main__":
    main()
