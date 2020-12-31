#!/usr/bin/python3
import operator
import sys, getopt
from time import sleep
import json
import os
import time
import signal
sys.path.append(os.getcwd())
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
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
from comm.result import result
from comm.error import error
from comm.parseargs import parseargs
from comm.functions import json_print
from vlsopt.violasclient import (
        violaswallet, 
        violasserver
        )
from vlsopt.violasproof import (
        violasproof
        )
from btc.btcclient import (
        btcclient
        )
from btc.btcwallet import (
        btcwallet
        )
from ethopt.ethclient import (
        ethclient,
        ethwallet
        )
from comm.values import(
        trantypebase as trantype,
        datatypebase as datatype
        )
from enum import Enum
from vrequest.request_client import requestclient
from analysis.analysis_filter import afilter
from dataproof import dataproof

name = "testmapping"
logger = log.logger.getLogger(name)
'''
violas or libra client
'''
def get_violasclient(chain = "violas"):
    if chain == "libra":
        return violasproof(name, stmanage.get_libra_nodes(), chain)
    return violasproof(name, stmanage.get_violas_nodes(), chain)

def get_violaswallet(chain = "violas"):
    return violaswallet(name, dataproof.wallets(chain), chain)

'''
ethereum client
'''
def get_ethclient(usd_erc20 = True, chain = "ethereum"):
    client = ethclient(name, stmanage.get_eth_nodes(), chain)
    client.load_vlsmproof(stmanage.get_eth_token("vlsmproof")["address"])
    if usd_erc20:
        tokens = client.get_token_list().datas
        logger.debug(f"support tokens: {tokens}")
        for token in tokens:
            client.load_contract(token)
    return client
    
def get_ethwallet(chain = "ethereum"):
    return ethwallet(name, dataproof.wallets("ethereum"), chain)

'''
btc client
'''

def getbtcclient():
    return btcclient(name, stmanage.get_btc_conn())

def getbtcwallet():
    return btcwallet(name, dataproof.wallets("btc"))

'''
proof client
'''
def get_proofclient(dtype = "e2vm"):
    return requestclient(name, stmanage.get_db(dtype))

def is_violas_tran_mark(dtype, datas):
    tran_data = json.loads(datas) if isinstance(datas, str) else datas
    data = json.loads(tran_data.get("data", {}))

    return data.get("flag") == "violas" and data.get("type") == f"{dtype}_mark"

def get_tran_id(dtype, datas):
    tran_data = json.loads(datas) if isinstance(datas, str) else datas
    data = json.loads(tran_data.get("data"))
    return data.get("tran_id")

def test_e2vm():

    ewallet = get_ethwallet()
    eclient = get_ethclient()
    vclient = get_violasclient()
    max_work_time = 180

    #send usdt token, to mapping violas-USDT
    from_address    = stmanage.get_map_address("e2vm", "ethereum")

    #proof contract, recevie approve
    to_address      = eclient.get_proof_contract_address("main").datas

    #will received violas-usdt, and set it to proof's datas
    vls_receiver    = stmanage.get_receiver_address_list("v2em", "violas")[0] #DD user

    #from these address get transaction, checkout exchange-e2vm transaction, get payment amount(usdt)
    vls_e2vm_senders  = stmanage.get_sender_address_list("e2vm", "violas") 


    ret = eclient.get_token_list()
    assert ret.state == error.SUCCEED, "get tokens failed."
    token_ids = ret.datas

    
    ret = ewallet.get_account(from_address)
    assert ret.state == error.SUCCEED, f"get account(from_address) failed"
    account = ret.datas

    for token_id in token_ids:
        if not work_continue():
            break

        start_time = time.time()
        ret = eclient.get_token_min_amount(token_id)
        assert ret.state == error.SUCCEED, f"get {token_id} min amount failed"
        amount = max(2000, ret.datas)

        ret = eclient.get_address_sequence(from_address)
        assert ret.state == error.SUCCEED, ret.message
        sequence = ret.datas

        ret = eclient.allowance(from_address, to_address, token_id)
        assert ret.state == error.SUCCEED, ret.message

        #make approve to 0
        if ret.datas > 0:
            ret = eclient.approve(account, to_address, 0, token_id)
            assert ret.state == error.SUCCEED, ret.message

        ret = eclient.approve(account, to_address, amount, token_id)
        assert ret.state == error.SUCCEED, ret.message
        eclient._logger.debug(f"allowance amount :{eclient.allowance(from_address, to_address, token_id).datas}")

        #get vls_e2vm_sender sequence before mapping e2vm
        vls_e2vm_senders_sequence = {}
        for sender in vls_e2vm_senders:
            ret = vclient.get_address_sequence(sender)
            assert ret.state == error.SUCCEED, ret.message
            vls_e2vm_senders_sequence.update({sender : ret.datas})

        #send proof to ethereum chain
        ret = eclient.send_proof(account, token_id, vls_receiver)
        assert ret.state == error.SUCCEED, ret.message
     
        #check sequence of from_address, make sure send_proof is succeed
        new_sequence = sequence
        while new_sequence <= sequence and work_continue():
            ret = eclient.get_address_sequence(from_address)
            assert ret.state == error.SUCCEED, ret.message
            new_sequence = ret.datas
            sleep(2)
            assert time.time() - start_time < max_work_time, f"time out, {from_address} sequence not changed"

        #get transaction info with from_address, sequence
        ret = eclient.get_transaction_version(from_address, new_sequence)
        assert ret.state == error.SUCCEED, ret.message
        version = ret.datas

        #wait state changed, get amount, usdt transfer maybe have transaction fee
        state = "start"
        map_amount = 0 
        while state == "start" and work_continue():
            ret = eclient.get_transactions(version, 1)
            assert ret.state == error.SUCCEED, ret.message
            tran = ret.datas[0]
            state = tran.get_state()
            map_amount = tran.get_amount()
            info = afilter.get_tran_data(tran, False)
            map_tran_id = get_tran_id("e2vm", info)
            
            sleep(2)
            assert time.time() - start_time < max_work_time, f"time out, eth proof {version} state not changed, check usdt transaction"

        #if state changed to end, check some value
        if state == "end":
            mapping_ok = False
            while not mapping_ok and work_continue():
                #check out mapping transaction
                for sender in vls_e2vm_senders:
                    if mapping_ok:
                        break
                    start_sequence = vls_e2vm_senders_sequence.get(sender) + 1
                    ret = vclient.get_address_sequence(sender)
                    assert ret.state == error.SUCCEED, f"get_address_sequence failed. {ret.message}"
                    latest_sequence = ret.datas
                    while (not mapping_ok) and start_sequence <= latest_sequence and work_continue():
                        ret = vclient.get_transaction_version(sender, start_sequence)
                        assert ret.state == error.SUCCEED, ret.message
                        new_version = ret.datas

                        ret = vclient.get_transactions(new_version, 1, True)
                        assert ret.state == error.SUCCEED, ret.message
                        tran = ret.datas[0] 
                        info = afilter.get_tran_data(tran, "violas")

                        start_sequence += 1
                        if not is_violas_tran_mark("e2vm", info):
                            vclient._logger.debug("not tran mark, check next...")
                            continue

                        tran_tran_id = get_tran_id("e2vm", info)
                        tran_receiver = info.get("receiver")
                        tran_sender  = info.get("sender")
                        tran_amount = info.get("amount")
                        tran_token_id = info.get("token_id")

                        if tran_tran_id == map_tran_id and vls_receiver == tran_receiver:
                            assert tran_amount == map_amount, "mapping amount is error. eth-{token_id} amount = {map_amount}, but violas-{tran_token_id} amount is {tran_amount}"
                            mapping_ok = True
                            print(f"mapping succeed. check violas address: version = {new_version}, receiver = {vls_receiver}, amount = {map_amount}")
                            return
                #else:
                #    assert False, f"not found transaction for mapping {token_id}, check tran_id = {map_tran_id} in {vls_e2vm_senders_sequence}"


def test_v2em():
    ewallet = get_ethwallet()
    eclient = get_ethclient()
    vclient = get_violasclient()
    vwallet = get_violaswallet()
    max_work_time = 180
    map_amount = 1_00_0000
    map_token_id = "USDT"
    eth_token_name = "usdt"

    #received eth-usdt address(mapping result)
    usdt_receiver = '0xf3FE0CB3b0c8Ab01631971923CEcDd14D857358A'
    
    #from this address send v2em request(violas transaction)
    from_address = stmanage.get_sender_address_list(datatype.E2VM, trantype.VIOLAS)[0]

    #receive v2em request, DD-account
    to_address = stmanage.get_receiver_address_list(datatype.V2EM, trantype.VIOLAS)[0]
    metadata = vclient.create_data_for_start(trantype.VIOLAS, datatype.V2EM, usdt_receiver)

    vclient._logger.debug(f'''
    usdt receiver = {usdt_receiver}
    send usdt address = {from_address}
    recever mapping receiver = to_address
    metadata = {metadata}
            ''')
    ret = vwallet.get_account(from_address)
    assert ret.state == error.SUCCEED, f"get {from_address} account failed. {ret.message}"
    map_sender = ret.datas

    before_usdt_amount = eclient.get_balance(usdt_receiver, eth_token_name).datas
    ret = vclient.send_coin(map_sender, to_address, map_amount, map_token_id, data = metadata)
    assert ret.state == error.SUCCEED, f"send coin faild from = {from_address} to_address = {to_address} metadata = {metadata}. {ret.message}"
    vclient._logger.debug(f"send coin result: {ret}")
    txn = ret.datas

    start_time = int(time.time())
    while start_time + max_work_time >= int(time.time()) and work_continue():
        after_usdt_amount = eclient.get_balance(usdt_receiver, eth_token_name).datas
        if after_usdt_amount > before_usdt_amount:
            vclient._logger.debug(f"mapping ok, mapping to {usdt_receiver} {eth_token_name} amount  {after_usdt_amount - before_usdt_amount}, input amount is {map_amount}")
            return
        print(f"\r\bRemaining time(s) = {max_work_time - int(time.time() - start_time)} will sleeping... 2 s", end = "") 
        sleep(2)

    if work_continue():
        assert False, f"time out, check bridge server is working...{txn}"

_work_continue = True
def signal_stop(signal, frame):
    try:
        global _work_continue
        print("start signal : %i", signal )
        _work_continue = False
    except Exception as e:
        parse_except(e)
    finally:
        print("end signal")

def work_continue():
    return _work_continue

def init_signal():
    signal.signal(signal.SIGINT, signal_stop)
    signal.signal(signal.SIGTSTP, signal_stop)
    signal.signal(signal.SIGTERM, signal_stop)

if __name__ == "__main__":
    stmanage.set_conf_env("../bvexchange.toml")
    init_signal()
    ##test_e2vm()
    test_v2em()

