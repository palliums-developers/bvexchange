#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append(os.getcwd())
sys.path.append("..")
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import stmanage
import requests
import random
import comm
import comm.error
import comm.result
import comm.values
from comm import version
from comm.result import result, parse_except
from comm.error import error
from enum import Enum
from baseobject import baseobject
from comm.functions import split_full_address
from comm.functions import (
        is_mnemonic,
        output_args
        )
from comm.values import (
        DECIMAL_VIOLAS,
        VIOLAS_ADDRESS_LEN,
        trantypebase as trantype,
        )

from dataproof import (
        dataproof,
        )
import redis


#module name
name="vclient"

class violaswallet(baseobject):
    
    def __init__(self, name, wallet_name, chain="violas"):
        assert wallet_name is not None, "wallet_name is None"
        baseobject.__init__(self, name, chain = chain)
        self.__wallet = None
        if wallet_name is not None:
            ret = self.__load_wallet(wallet_name, chain)
            if ret.state != error.SUCCEED:
                raise Exception(f"load wallet[{wallet_name}] failed.")

    def __del__(self):
        pass

    def __load_wallet(self, wallet, chain="violas"):
        try:
            if chain in ("violas"):
                from vlsopt.violasproxy import walletproxy
            elif chain in ("libra"):
                from vlsopt.libraproxy import walletproxy
            elif chain in ("diem"):
                from vlsopt.diemproxy import walletproxy
            else:
                raise Exception(f"chain name[{chain}] unkown. can't connect libra/violas wallet")

            self.__wallet_name = wallet
            if isinstance(wallet, str) and os.path.isfile(wallet):
                self.__wallet = walletproxy.load(wallet)
                ret = result(error.SUCCEED, "", "")
            elif is_mnemonic(wallet):
                self.__wallet_name = None #not save to file
                self.__wallet = walletproxy.loads(wallet)
                ret = result(error.SUCCEED, "", "")
            else:
                ret = result(error.SUCCEED, "not found wallet file", "")
                raise Exception(f"not found {self.name()} wallet file({self.__wallet_name})")

        except Exception as e:
            ret = parse_except(e)
        return ret

    def save(self):
        try:
            if self.__wallet is not None and self.__wallet_name:
                self.__wallet.write_recovery(self.__wallet_name)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    @classmethod
    def is_valid_address(self, address):
        try:
            ret = result(error.SUCCEED, datas = len(address) in VIOLAS_ADDRESS_LEN)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def dump_wallet(self):
        try:
            if self.__wallet is not None:
                self.save()
                self.__wallet = None
                pass
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def new_account(self):
        try:
            account = self.__wallet.new_account();
            self.save()
            ret = result(error.SUCCEED, "", account)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_account_count(self):
        return len(self.__wallet.accounts)

    def get_wallet_address(self, address):
        try:
            (auth, addr) = split_full_address(address)
            ret = result(error.SUCCEED, datas = self.__wallet.map_to_wallet_address(auth))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_account(self, addressorid):
        try:
            address = addressorid
            if isinstance(addressorid, str) and len(addressorid) >= min(VIOLAS_ADDRESS_LEN):
                auth, address = self.split_full_address(addressorid).datas

            account = self.__wallet.get_account_by_address_or_refid(address)
            if account is None:
                ret = result(error.ARG_INVALID)
            else:
                ret = result(error.SUCCEED, "", account)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def find_account_by_address_hex(self, address):
        (auth, addr) = self.split_full_address(address).datas
        for i in range(len(self.__wallet.accounts)):
            if self.__wallet.accounts[i].address.hex() == addr:
                return (i, self.__wallet.accounts[i])

        return (-1, None)

    @output_args
    def has_account_by_address(self, address):
        try:
            _, account = self.find_account_by_address_hex(address)
            if account is None:
                ret = result(error.SUCCEED, "", False)
            else:
                ret = result(error.SUCCEED, "", True)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def has_account(self):
        try:
            self.__wallet.get_account_by_address_or_refid(0)
            ret = result(error.SUCCEED, "", True)
        except ValueError as e: #account count is 0, so not found account
            ret = result(error.SUCCEED, "", False)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def split_full_address(self, address, auth_key_prefix = None):
        try:
            auth, addr = split_full_address(address, auth_key_prefix)
            ret = result(error.SUCCEED, datas = (auth, addr))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def sign_message(self, address, message):
        try:
            ret = self.get_account(address)
            if ret.state != error.SUCCEED:
                return ret
            sigger = ret.datas
            data = message
            if isinstance(message, str):
                data = message.encode()
            
            ret = result(error.SUCCEED, datas=sigger.sign(data).hex())
        except Exception as e:
            ret = parse_except(e)
        return ret

    def __getattr__(self, name):
        self.__call = getattr(self.__wallet, name)
        return self.__call

    def __call__(self, *args, **kwargs):
        #return self.__call(*args, **kwargs)
        pass

class violasclient(baseobject):
    class role_id(Enum):
        DD_ACCOUNT  = 2
        PARENT_VASP = 5
        CHILD_VASP  = 6
        UNKOWN      = sys.maxsize

    def __init__(self, name, nodes, chain = "violas", use_faucet_file = False):
        baseobject.__init__(self, name, chain = chain)
        self.__client = None
        self.__node = None
        if nodes is not None:
            ret = self.conn_node(name, nodes, chain, use_faucet_file = use_faucet_file)
            if ret.state != error.SUCCEED:
                raise Exception(f"connect {chain} node failed.")

    def __del__(self):
        self.disconn_node()


    def clientname(self):
        return self.__client.clientname()

    def conn_node(self, name, nodes, chain = "violas", use_faucet_file = False):
        try:
            if nodes is None or len(nodes) == 0:
                return result(error.ARG_INVALID, repr(nodes), "")
            
            if chain in ("violas"):
                from vlsopt.violasproxy import violasproxy as clientproxy
            elif chain in ("libra"):
                from vlsopt.libraproxy import libraproxy as clientproxy
            elif chain in (trantype.DIEM.value):
                from vlsopt.diemproxy import diemproxy as clientproxy
            else:
                raise Exception(f"chain name[{chain}] unkown. can't connect libra/violas node")

            for node in nodes:
                try:
                    if self.work() == False:
                        return result(error.FAILED, f"connect {chain} work stop")

                    self._logger.debug("try connect node({}) : host = {} port = {} validator={} faucet ={}".format( \
                            node.get("name", ""), node.get("host"), node.get("port"), node.get("validator"), node.get("faucet")))
                    client = clientproxy.connect(host=node.get("host"), \
                            port=node.get("port"), \
                            faucet_file = node.get("faucet"), \
                            timeout = node.get("timeout"), \
                            debug = node.get("debug", False), \
                            use_faucet_file = use_faucet_file)
                    client.get_latest_version()
                    self._logger.debug(f"connect {chain} node succeed.") 
                except Exception as e:
                    parse_except(e)
                    self._logger.info(f"connect {chain} node failed({e}). test next...")
                else:
                    self.__client = client
                    self.__node = node
                    return result(error.SUCCEED, "", "")

            #not connect any violas node
            ret = result(error.FAILED,  f"connect {chain} node failed.", "")
        except Exception as e:
            ret = parse_except(e)
        return ret
    
    def stop(self):
        self.work_stop()

    def disconn_node(self):
        try:
            ret = result(error.SUCCEED) 
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_decimals(self, nouse = None):
        return DECIMAL_VIOLAS

    def token_id_effective(self, token_id):
        try:
            token_list = self.__client.get_registered_currencies()
            ret = result(error.SUCCEED, datas = token_id in token_list)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_token_list(self, address = None):
        try:
            token_list = self.__client.get_registered_currencies()
            if address is not None:
                ret = self.get_account_state(address)
                if ret.state != error.SUCCEED:
                    return ret
                if ret.datas is not None:
                    token_list = [token_id for token_id in token_list if ret.datas.is_published(token_id)]
                else:
                    token_list = []
            ret = result(error.SUCCEED, datas = token_list)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def bind_token_id(self, account, token_id, gas_token_id):
        try:
            datas = self.__client.add_currency_to_account(account, token_id, gas_currency_code = gas_token_id)
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def has_token_id(self, address, token_id):
        try:
            state = False
            ret = self.get_account_state(address)
            if ret.state != error.SUCCEED:
                return ret
            ret = result(error.SUCCEED, datas = ret.datas is not None and ret.datas.is_published(token_id))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def split_full_address(self, address, auth_key_prefix = None):
        try:
            if address and self.chain == trantype.DIEM.value and len(address) not in VIOLAS_ADDRESS_LEN:
                return result(error.SUCCEED, datas = (None, address))

            datas = split_full_address(address, auth_key_prefix)
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def mint_coin(self, address, amount, token_id, module = None, auth_key_prefix = None, is_blocking=True):
        try:
            (auth, addr) = self.split_full_address(address, auth_key_prefix).datas
            (_, mod) = self.split_full_address(module).datas

            self.__client.mint_coin(receiver_address = addr, micro_coins = amount, currency_code = token_id, currency_module_address = mod, auth_key_prefix = auth, is_blocking=is_blocking)
            ret = result(error.SUCCEED) 
        except Exception as e:
            ret = parse_except(e)
        return ret

    def send_violas_coin(self, from_account, to_address, amount, token_id, module_address = None, data=None, auth_key_prefix = None, is_blocking=True, max_gas_amount = 100_0000, gas_token_id = None):
        return self.send_coin(from_account, to_address, amount, token_id, module_address, data, auth_key_prefix, is_blocking, max_gas_amount, gas_token_id = gas_token_id)

    def check_address_has_token_id(self, address, token_id):
        try:
            ret = self.has_token_id(address, token_id)
            if ret.state != error.SUCCEED:
                return ret

            if not ret.datas:
                return result(error.ARG_INVALID, f"account ({address}) not bind token({token_id})")

            ret = result(error.SUCCEED, datas = True)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def send_coin(self, from_account, to_address, amount, token_id, module_address = None, data=None, auth_key_prefix = None, is_blocking=True, max_gas_amount = 100_0000, gas_token_id = None, *args, **kwargs):
        try:
            if (len(to_address) not in VIOLAS_ADDRESS_LEN) or amount < 1:
                return result(error.ARG_INVALID, f"args is invalid check to_address({len(to_address)} is in {VIOLAS_ADDRESS_LEN}): {to_address} and amount(> 0): {amount}")

            (_, mod) = self.split_full_address(module_address).datas
            module_address = None

            (auth, addr) = self.split_full_address(to_address, auth_key_prefix).datas
            (_, module_addr) = self.split_full_address(module_address).datas

            #set gas_token_id, default : Violas = VLS
            gas_token_id = gas_token_id if gas_token_id else dataproof.configs("gas_token_id").get(self.chain)

            self._logger.debug(f"send_coin(from_account={from_account.address.hex()} to_address={to_address} amount = {amount} token_id = {token_id} module_address={module_address} data = {data} auth_key_prefix = {auth_key_prefix} max_gas_amount = {max_gas_amount}, gas_token_id = {gas_token_id})")

            ret = self.check_address_has_token_id(from_account.address.hex(), token_id)
            if ret.state != error.SUCCEED:
                return ret

            ret = self.check_address_has_token_id(to_address, token_id)
            if ret.state != error.SUCCEED:
                return ret

            self.__client.send_coin(sender_account=from_account, receiver_address=addr, \
                    micro_coins=amount, token_id = token_id, module_address=module_addr, \
                    data=data, auth_key_prefix = auth_key_prefix, is_blocking=is_blocking, max_gas_amount = max_gas_amount, gas_token_id = gas_token_id)
            ret = result(error.SUCCEED, datas="") 
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_violas_balance(self, account_address, token_id = None, module_address = None):
        return self.get_balance(account_address, token_id, module_address)

    def get_balance(self, account_address, token_id = None, module_address = None):
        try:
            (_, addr) = self.split_full_address(account_address).datas
            (_, module_addr) = self.split_full_address(module_address).datas

            balance = self.__client.get_balance(account_address = addr, currency_code = token_id, currency_module_address = module_addr)
            ret = result(error.SUCCEED, "", balance)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_balances(self, account_address):
        try:
            (_, addr) = self.split_full_address(account_address).datas

            balance = self.__client.get_balances(account_address = addr)
            ret = result(error.SUCCEED, "", balance)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_account_state(self, address, module = None):
        try:
            (_, addr) = self.split_full_address(address).datas
            (_, mod) = self.split_full_address(module).datas
            state =  self.__client.get_account_state(addr)
            ret = result(error.SUCCEED, "", state)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_address_sequence(self, address):
        try:
            (_, addr) = self.split_full_address(address).datas
            num = self.__client.get_sequence_number(addr)
            ret = result(error.SUCCEED, "", num - 1)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_transaction_version(self, address, sequence):
        try:
            (_, addr) = self.split_full_address(address).datas
            num = self.__client.get_account_transaction(addr, sequence).get_version()
            ret = result(error.SUCCEED, "", num)
        except Exception as e:
            ret = parse_except(e)
        return ret
    def get_address_version(self, address):
        try:
            (_, addr) = self.split_full_address(address).datas
            ret = self.get_address_sequence(addr)
            if ret.state != error.SUCCEED:
                return ret

            ret = self.get_transaction_version(address, ret.datas)
            if ret.state != error.SUCCEED:
                return ret

            ret = result(error.SUCCEED, "", ret.datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_latest_transaction_version(self):
        try:
            datas = self.__client.get_latest_version()
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_transactions(self, start_version, limit = 1, fetch_event=True):
        try:
            datas = self.__client.get_transactions(int(start_version), limit, fetch_event)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_transaction(self, version, fetch_event=True):
        try:
            datas = self.__client.get_transactions(version, 1 , fetch_event)
            ret = result(error.SUCCEED, "", datas[0] if datas is not None else None)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_account_transactions(self, address, start, limit, include_events = True):
        '''
        @dev get account transactions 
        @param address hex-encoded account address
        @param start the start of account sequence number
        @param limit the maximum number of transactions to return 
        @param include_events set true to also fetch events generated by the transaction
        @return array of transaction
        '''
        try:
            (_, addr) = self.split_full_address(address).datas
            datas = self.__client.get_account_transactions(addr, int(start), int(limit), include_events)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret


    def get_account_role_id(self, address):
        try:
            ret = self.get_account_state(address)
            if ret.state != error.SUCCEED:
                return ret
            ret = result(error.SUCCEED, "", ret.datas.get_role_id() if ret.datas else self.role_id.UNKOWN)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def check_account_is_registered(self, address):
        try:
            ret = self.get_account_role_id(address)
            if ret.state != error.SUCCEED:
                return ret
            
            ret = result(error.SUCCEED, "", ret.datas !=  self.role_id.UNKOWN)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_account_role_name(self, address):
        try:
            ret = self.get_account_role_id(address)
            if ret.state != error.SUCCEED:
                return ret
            ret = result(error.SUCCEED, "", self.role_id(ret.datas).name)
        except Exception as e:
            ret = result(error.SUCCEED, "", "unkown")
        return ret

    def check_account_is_dd(self, address):
        try:
            ret = self.get_account_role_id(address)
            if ret.state != error.SUCCEED:
                return ret
            
            ret = result(error.SUCCEED, "", self.role_id(ret.datas) == self.role_id.DD_ACCOUNT)
        except Exception as e:
            ret = parse_except(e)
        return ret


    def check_account_is_parent_vasp(self, address):
        try:
            ret = self.get_account_role_id(address)
            if ret.state != error.SUCCEED:
                return ret
            
            ret = result(error.SUCCEED, "", self.role_id(ret.datas) == self.role_id.PARENT_VASP)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def check_account_is_child_vasp(self, address):
        try:
            ret = self.__client.get_account_role_id(address)
            if ret.state != error.SUCCEED:
                return ret
            
            ret = result(error.SUCCEED, "", self.role_id(ret.datas) == self.role_id.CHILD_VASP)
        except Exception as e:
            ret = parse_except(e)
        return ret

    '''
    * https://github.com/diem/diem/blob/master/json-rpc/docs/method_get_events.md
    '''
    def get_events(self, key, start = 0, limit = 10):
        try:
            datas = self.__client.get_events(key, start, limit)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    '''
    * https://github.com/diem/diem/blob/master/json-rpc/docs/method_get_events_with_proof.md
    '''
    def get_events_with_proof(self, key, start = 0, limit = 10):
        try:
            datas = self.__client.get_events_with_proof(key, start, limit)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    '''
    * https://github.com/diem/diem/blob/master/json-rpc/docs/method_get_metadata.md
    '''
    def get_metadata(self, version):
        try:
            datas = self.__client.get_metadata(version)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    #*************************************swap functions ************************************************
    def swap(self, sender_account, token_in, token_out, amount_in, amount_out_min=0, receiver = None, is_blocking=True, **kwargs):
        try:
            self._logger.debug(f"swap({sender_account.address.hex()}, {token_in}, {token_out}, {amount_in}, {amount_out_min}, {receiver})")
            (_, addr) = self.split_full_address(receiver).datas
            if "gas_currency_code" not in kwargs:
                kwargs.update({"gas_currency_code":token_in})


            ret = self.check_address_has_token_id(sender_account.address.hex(), token_in)
            if ret.state != error.SUCCEED:
                return ret

            ret = self.check_address_has_token_id(receiver, token_out)
            if ret.state != error.SUCCEED:
                return ret

            datas = self.__client.swap(sender_account = sender_account, currency_in = token_in, currency_out = token_out, \
                    amount_in = amount_in, amount_out_min = amount_out_min, receiver_address = addr, is_blocking = is_blocking, **kwargs)
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret


    def swap_set_module_address(self, address, **kwargs):
        try:
            (_, addr) = self.split_full_address(address).datas
            datas = self.__client.set_exchange_module_address(addr)
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def swap_publish_contract(self, account, **kwargs):
        try:
            datas = self.__client.swap_publish_contract(account, **kwargs)
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def swap_initialize(self, account, **kwargs):
        try:
            datas = self.__client.swap_initialize(account, **kwargs)
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def swap_add_currency(self, account, token_id, **kwargs):
        try:
            datas = self.__client.swap_add_currency(account, token_id, gas_currency_code = token_id)
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def swap_add_liquidity(self, account, token_a, token_b, amount_desired_a, amount_desired_b, amount_min_a = 0, amount_min_b = 0, is_blocking = True, **kwargs):
        try:
            datas = self.__client.swap_add_liquidity(account, token_a, token_b, amount_desired_a, amount_desired_b, amount_min_a, amount_min_b, is_blocking = is_blocking, **kwargs)
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def swap_get_output_amount(self, token_in, token_out, amount_in, **kwargs):
        try:
            datas = self.__client.swap_get_swap_output_amount(token_in, token_out, amount_in, **kwargs)
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def swap_get_input_amount(self, token_in, token_out, amount_in, **kwargs):
        try:
            datas = self.__client.swap_get_swap_in_amount(token_in, token_out, amount_in, **kwargs)
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def swap_get_liquidity_balances(self, address, **kwargs):
        try:
            (_, addr) = self.split_full_address(address).datas
            datas = self.__client.swap_get_liquidity_balances(addr)
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def swap_remove_liquidity(self, account, token_a, token_b, liquidity, amount_min_a = 0, amount_min_b = 0, is_blocking = True, **kwargs):
        try:
            datas = self.__client.swap_remove_liquidity(account, token_a, token_b, liquidity, amount_min_a, amount_min_b, is_blocking = is_blocking, **kwargs)
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def swap_get_reserves_resource(self, address):
        try:
            dates = None
            ret = self.get_account_state(address)
            if ret.state != error.SUCCEED:
                return ret

            account_state = ret.datas
            if account_state is not None:
                datas = account_state.swap_get_reserves_resource()
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def swap_is_swap_address(self, address):
        try:
            (_, addr) = self.split_full_address(address).datas
            ret = self.swap_get_reserves_resource(addr)
            ret = result(ret.state, datas = ret.datas is not None)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def swap_get_registered_tokens(self):
        try:
            datas = self.__client.swap_update_registered_currencies()
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def swap_set_owner_address(self, address):
        try:
            datas = self.__client.set_exchange_owner_address(address)
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def create_child_vasp_account(self, parent_vasp_account, child_address, auth_key_prefix, currency_code="VLS", add_all_currency=False,
                                  child_initial_balance=0, gas_token_id="VLS", **kwargs):
        try:
            (auth, addr) = split_full_address(child_address)
            if auth_key_prefix:
                auth = auth_key_prefix

            datas = self.__client.create_child_vasp_account(parent_vasp_account, addr, auth, currency_code, \
                    add_all_currency, child_initial_balance, gas_token_id, **kwargs)
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_associate_account(self):
        return self.__client.associate_account

    def get_associate_address(self):
        return self.__client.associate_account.address_hex

class violasserver(baseobject):
    __node = None
    def __init__(self, name, nodes):
        baseobject.__init__(self, name)
        self.__server = None
        assert nodes is not None, "nodes is None"
        if nodes is not None:
            ret = self.conn_node(nodes)
            if ret.state != error.SUCCEED:
                raise Exception("connect violas servier failed.")

    def __del__(self):
        self.disconn_node()

    def conn_node(self, nodes):
        try:
            if nodes is None or len(nodes) == 0:
                return result(error.ARG_INVALID, repr(nodes), "")
            
            for node in nodes:
                try:
                    server = ""
                    #server = Client.new(node["host"], node["port"], node["user"], node["password"])
                    self._logger.debug("connect violas server: host= {} port = {} user={} password=******".format( \
                            node.get("host"), node.get("port"), node.get("user")))
                    self.__node = node
                except Exception as e:
                    parse_except(e)
                else:
                    self.__server = server 
                    self.__node = node
                    return result(error.SUCCEED, "", "")

            #not connect any violas node
            ret = result(error.FAILED,  "connect violas node failed.", "")
        except:
            ret = parse_except(e)
        return ret
    
    def disconn_node(self):
        try:
            ret = result(error.SUCCEED) 
        except Exception as e:
            ret = parse_except(e)
        return ret
   
    def has_transaction(self, address, module, baddress, sequence, amount, version, receiver):
        try:
            ret = result(error.FAILED, "", "")
            data = {
                    "version":version,
                    "sender_address":address,
                    "sequence_number":sequence,
                    "amount":amount,
                    "to_address":baddress,
                    "module":module,
                    "receiver":receiver,
                    }
            url = "http://{}:{}/1.0/violas/vbtc/transaction".format(self.__node["host"], self.__node["port"])
            headers = headers = {'Content-Type':'application/json'}
            response = requests.post(url,  json = data)
            if response is not None:
                jret = json.loads(response.text)
                if jret["code"] == 2000:
                    ret = result(error.SUCCEED, jret["message"], True)
                else:
                    ret = result(error.SUCCEED, jret["message"], False)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def create_child_vasp_account(self, address, auth_key_prefix):
        try:
            ret = result(error.FAILED, "", "")
            data = {
                    "address":address,
                    "auth_key_prefix":auth_key_prefix,
                    }
            #https://api4.violas.io/1.0/violas/mint?address=4ba8309ef7d504851ff0018792756c59&auth_key_perfix=053ee0194d34396f582ddf091ce44de7
            auth, addr = split_full_address(address)
            auth = auth_key_prefix if auth is None else auth
            url = f"https://{self.__node['host']}/1.0/violas/mint?address={addr}&auth_key_perfix={auth}"
            response = requests.get(url)
            if response is not None:
                jret = json.loads(response.text)
                if jret["code"] == 2000:
                    ret = result(error.SUCCEED, jret["message"], True)
                else:
                    ret = result(error.SUCCEED, jret["message"], False)
        except Exception as e:
            ret = parse_except(e)
        return ret





def main():
    pass
if __name__ == "__main__":
    main()
