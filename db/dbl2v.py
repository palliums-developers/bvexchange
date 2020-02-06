#!/usr/bin/python3
'''
btc exchange vtoken db
'''
import operator
import sys,os
sys.path.append(os.getcwd())
sys.path.append("..")
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import stmanage
import random
from comm.error import error
from comm.result import result
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, UniqueConstraint, Index, String

from baseobject import baseobject
from enum import Enum

#module name
name="dbl2v"

class dbl2v(baseobject):
    __base = declarative_base()
    __engine = ""
    __session = ""
    __engine = ""

    def __init__(self, name, dbfile):
        baseobject.__init__(self, name)
        self.__init_db(dbfile)

    def __del__(self):
        self.__uninit_db()

    #btc exchange vtoken state
    #state change case:  
    ##SUCCEED->COMPLETE
    ##SUCCEED->VFAILED->SUCCEED->COMPLETE
    ##FAILED->SUCCEED->COMPLETE
    ##FAILED->SUCCEED->VFAILED->SUCCEED->COMPLETE
    class state(Enum):
        START       = 0  #no use
        SUCCEED     = 1  #send btc ok and send change state transaction succeed but not confirm
        FAILED      = 2  #send btc failed
        VFAILED     = 3  #send change state transaction failed
        VSUCCEED    = 4  #send change state transaction succeed
        COMPLETE    = 6  #change state is confirmed
    
    #exc_traceback_objle : v2binfo
    class v2binfo(__base):
        __tablename__='l2vinfo'
        fromaddress = Column(String(64), index=True, nullable=False) #libra address
        toaddress   = Column(String(64), index=True, nullable=False) #libra address
        sequence    = Column(Integer, index=True, nullable=False)
        version     = Column(Integer, index=True, nullable=False, primary_key=True)
        amount      = Column(Integer, nullable=False)
        receiver    = Column(String(64), index=True, nullable=False)
        module      = Column(String(64), nullable=False)
        state       = Column(Integer, index=True, nullable=False)
        created     = Column(DateTime, default=datetime.datetime.now)
        times       = Column(Integer, nullable=False, default=1)
        tranid      = Column(String(64), nullable=False, primary_key=True)
    
        def __repr__(self):
            return f"<v2binfo(fromaddress={self.fromaddress}, toaddress={self.toaddress}, sequence={self.sequence}, \
                    version={self.version}, amount={self.amount}, receiver={self.receiver}, module={self.module}, state={self.state}, \
                    created={self.created}, times={self.times}, tranid={self.tranid})>"

    def __init_db(self, dbfile):
        self._logger.debug("start __init_db(dbfile={})".format(dbfile))
        db_echo = False

        if stmanage.get_db_echo():
            db_echo = stmanage.get_db_echo()

        self.__engine = create_engine('sqlite:///%s?check_same_thread=False' % dbfile, echo=db_echo)
        #self.v2binfo.__table__
        self.__base.metadata.create_all(self.__engine)
        Session = sessionmaker(bind=self.__engine)
        self.__session = Session()
    
    def __uninit_db(self):
        pass
        
    def insert(self, fromaddress, toaddress, sequence, version, amount, receiver, module, state, tranid):
        try:
            self._logger.info(f"start insert(fromaddress={fromaddress}, toaddress={toaddress}, \
                    sequence={sequence}, version={version}, amount={amount}, module={module}, state={state.name}, tranid={tranid})") 

            data = self.v2binfo(fromaddress=fromaddress, toaddress=toaddress, sequence=vsequence, version=version, \
                amount=amount, receiver=receiver, module=module, state=state.value, tranid=tranid)
            self.__session.add(data)

            ret = result(error.SUCCEED, "", "")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def insert_commit(self, fromaddress, toaddress, sequence, version, amount, receiver, module, state, tranid):
        try:
            ret = self.insert(fromaddress, toaddress, sequence, version, amount, receiver, module, state, tranid)
            if ret.state != error.SUCCEED:
                return ret 
            ret = self.commit()
        except Exception as e:
            ret = parse_except(e)
        return ret

    def commit(self):
        try:
            self._logger.debug("start commit")
            self.__session.flush()
            self.__session.commit()

            ret = result(error.SUCCEED, "", "")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def query(self, tranid):
        proofs = []
        try:
            self._logger.debug(f"start query(tranid={tranid})")
            filter_tranid = (self.v2binfo.tranid==tranid)
            proofs = self.__session.query(self.v2binfo).filter(filter_tranid).all()
            ret = result(error.SUCCEED, "", proofs)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def has_info(self, tranid):
        try:
            self._logger.debug(f"start has_info(tranid={tranid})")
            filter_tranid = (self.v2binfo.tranid==tranid)
            state = (self.__session.query(self.v2binfo).filter(filter_tranid).count() > 0)
            ret = result(error.SUCCEED, "", state) 
        except Exception as e:
            ret = parse_except(e)
        return ret


    def __query_state(self, state, maxtimes=999999999):
        proofs = []
        try:
            self._logger.debug(f"start __query_state(state={state}, maxtimes={maxtimes})")
            filter_state = (self.v2binfo.state==state.value)
            filter_times = (self.v2binfo.times<=maxtimes)
            proofs = self.__session.query(self.v2binfo).filter(filter_state).filter(filter_times).all()
            ret = result(error.SUCCEED, "", proofs)
            self._logger.debug(f"result: {len(ret.datas)}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def query_is_start(self, maxtimes = 999999999):
        return self.__query_state(self.state.START, maxtimes)

    def query_is_succeed(self, maxtimes = 999999999):
        return self.__query_state(self.state.SUCCEED, maxtimes)

    def query_is_failed(self, maxtimes=999999999):
        return self.__query_state(self.state.FAILED, maxtimes)

    def query_is_complete(self, maxtimes=999999999):
        return self.__query_state(self.state.COMPLETE, maxtimes)

    def query_is_vfailed(self, maxtimes=999999999):
        return self.__query_state(self.state.VFAILED, maxtimes)

    def query_is_vsucceed(self, maxtimes = 999999999):
        return self.__query_state(self.state.VSUCCEED, maxtimes)

    def __update(self, tranid, state):
        try:
            self._logger.info(f"start update(tranid={tranid}, state={state}, txid={txid})")
            filter_tranid = (self.v2binfo.tranid==tranid)
            datas = self.__session.query(self.v2binfo).filter(filter_tranid)\
                    .update({self.v2binfo.state:state.value, self.v2binfo.times:self.v2binfo.times + 1})
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def __update_commit(self, tranid, state):
        try:
            ret = self.__update(tranid, state)
            if ret.state != error.SUCCEED:
                self._logger.error("update_v2binfo_commit failed")
                return ret

            ret = self.commit()
        except Exception as e:
            ret = parse_except(e)
        return ret

    def update_to_start_commit(self, tranid):
        return self.__update_commit(tranid, self.state.START)

    def update_to_succeed_commit(self, tranid):
        return self.__update_commit(tranid, self.state.SUCCEED)

    def update_to_failed_commit(self, tranid):
        return self.__update_commit(tranid, self.state.FAILED)

    def update_to_complete_commit(self, tranid):
        return self.__update_commit(tranid, self.state.COMPLETE)

    def update_to_vfailed_commit(self, tranid):
        return self.__update_commit(tranid, self.state.VFAILED)

    def update_to_vsucceed_commit(self, tranid):
        return self.__update_commit(tranid, self.state.VSUCCEED)

def show_state_count(db):
    ret = db.query_is_start()
    assert ret.state == error.SUCCEED, "query failed."
    self._logger.debug(f"query_is_start:{ret.datas}")

    ret = db.query_is_succeed()
    assert ret.state == error.SUCCEED, "query failed."
    self._logger.debug(f"query_is_succeed:{ret.datas}")

    ret = db.query_is_failed()
    assert ret.state == error.SUCCEED, "query failed."
    self._logger.debug(f"query_is_failed:{ret.datas}")

    ret = db.query_is_complete()
    assert ret.state == error.SUCCEED, "query failed."
    self._logger.debug(f"query_is_complete:{ret.datas}")

    ret = db.query_is_vfailed()
    assert ret.state == error.SUCCEED, "query failed."
    self._logger.debug(f"query_is_vfailed:{ret.datas}")

    ret = db.query_is_vsucceed()
    assert ret.state == error.SUCCEED, "query failed."
    self._logger.debug(f"query_is_vsucceed:{ret.datas}")


def test_dbl2v():
    pass
    db = dbl2v("test_dbl2v", "test_dbl2v.db")
    ret = db.insert_commit("b50323341dd6e996d7add7777af0de640ffe1407828cd7db625097b40e6a2c78", \
            "29223f25fe4b74d75ca87527aed560b2826f5da9382e2fb83f9ab740ac40b8f7",\
            9, \
            9999, \
            1000, \
            "fd0426fa9a3ba4fae760d0f614591c61bb53232a3b1138d5078efa11ef07c49c", \
            "61b578c0ebaad3852ea5e023fb0f59af61de1a5faf02b1211af0424ee5bbc410", \
            dbl2v.state.START, \
            "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            )
    assert ret.state == error.SUCCEED, "insert_commit failed."

    db.insert_commit("b50323341dd6e996d7add7777af0de640ffe1407828cd7db625097b40e6a2c78", \
            "29223f25fe4b74d75ca87527aed560b2826f5da9382e2fb83f9ab740ac40b8f7",\
            10, \
            99998, \
            2000, \
            "fd0426fa9a3ba4fae760d0f614591c61bb53232a3b1138d5078efa11ef07c49c", \
            "61b578c0ebaad3852ea5e023fb0f59af61de1a5faf02b1211af0424ee5bbc410", \
            dbl2v.state.START, \
            "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv"
            )
    assert ret.state == error.SUCCEED, "insert_commit failed."

    ret = db.query("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    assert ret.state == error.SUCCEED, "query failed."
    self._logger.debug(f"query result: {ret.datas}")

    self._logger.debug(f"has info(true):{db.has_info(\"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\")}")
    self._logger.debug(f"has info(false):{db.has_info(\"VVVVVVVVVVVVVVVVVVVVVVVVV\")}")
    
    show_state_count(db)
    tran_id = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

    ret = db.update_to_failed_commit(tran_id)
    show_state_count(db)

    ret = db.update_to_succeed_commit(tran_id)
    show_state_count(db)

    ret = db.update_to_start_commit(tran_id)
    show_state_count(db)

    ret = db.update_to_vfailed_commit(tran_id)
    show_state_count(db)

    ret = db.update_to_vsucceed_commit(tran_id)
    show_state_count(db)

    ret = db.update_to_complete_commit(tran_id)
    show_state_count(db)
if __name__ == "__main__":
    test_dbl2v()
