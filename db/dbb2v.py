#!/usr/bin/python3
'''
btc exchange vbtc db
'''
import operator
import sys
sys.path.append("..")
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import setting
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, UniqueConstraint, Index, String

from enum import Enum

#module name
name="dbb2v"

#load logging
logger = log.logger.getLogger("dblog") 

class dbb2v:
    __base = declarative_base()
    __engine = ""
    __session = ""
    __engine = ""
    __traceback_limit = 0

    def __init__(self, dbfile, traceback_limit):
        logger.debug("start __init__")
        self.__traceback_limit = traceback_limit
        self.__init_db(dbfile)

    def __del__(self):
        logger.debug("start __del__")
        self.__uninit_db()

    #btc exchange vbtc state
    class state(Enum):
        START = 0
        SUCCEED = 1
        FAILED = 2
    
    #exc_traceback_objle : b2vinfo
    class b2vinfo(__base):
        __tablename__='b2vinfo'
        txid        = Column(String(64), index=True, nullable=False)
        fromaddress = Column(String(64), index=True, nullable=False)
        toaddress   = Column(String(64), index=True, nullable=False)
        bamount     = Column(Integer, nullable=False)
        vaddress    = Column(String(64), index=True, nullable=False, primary_key=True)
        sequence    = Column(Integer, index=True, nullable=False, primary_key=True)
        vamount     = Column(Integer)
        vbtc        = Column(String(64), nullable=False)
        createblock = Column(String(64), index=True, nullable=False)
        updateblock = Column(String(64), index=True)
        state       = Column(Integer, index=True, nullable=False)
        created     = Column(DateTime, default=datetime.datetime.now)
    
        def __repr__(self):
            return "<b2vinfo(txid=%s,fromaddress = %s, toaddress = %s, bamount = %i, vaddress = %s, sequence=%i, \
                    vamount = %i, vbtc = %s, createblock = %s, updateblock = %s, state = %i)>" % (
                    self.txid, self.fromaddress, self.toaddress, self.bamount, self.vaddres, self.sequence, \
                    self.vamount, self.vbt, self.createblock, self.updateblock, self.state)
    
    def __init_db(self, dbfile):
        logger.debug("start __init_db")
        db_echo = False

        if setting.db_echo:
            db_echo = setting.db_echo

        self.__engine = create_engine('sqlite:///%s?check_same_thread=False' % dbfile, echo=db_echo)
        #self.b2vinfo.__table__
        self.__base.metadata.create_all(self.__engine)
        Session = sessionmaker(bind=self.__engine)
        self.__session = Session()
    
    def __uninit_db(self):
        logger.debug("start __uninit_db")
        
    def insert_b2vinfo(self, vtxid, vfromaddress, vtoaddress, vbamount, vvaddress, vsequence, vvamount, vvbtc, vcreateblock, vupdateblock):
        try:
            logger.debug("start insert_b2vinfo (vtxid, vfromaddress, vtoaddress, vbamount, vvaddress, vsequence, vvamount, vvbtc, vcreateblock, vupdateblock, vstate),  \
                    value(%s, %s, %s, %i, %s %i, %i, %s, %s, %s, %s)" % \
                    (vtxid, vfromaddress, vtoaddress, vbamount, vvaddress, vsequence, vvamount, vvbtc, vcreateblock, vupdateblock, self.state.START.name))

            b2vi = self.b2vinfo(txid=vtxid, fromaddress=vfromaddress, toaddress=vtoaddress, bamount=vbamount, vaddress=vvaddress, sequence=vsequence, \
                vamount=vvamount, vbtc=vvbtc, createblock=vcreateblock, updateblock=vupdateblock, state=self.state.START.value)
            self.__session.add(b2vi)

            return True
        except Exception as e:
            logger.error(traceback.format_exc(limit=self.__traceback_limit))
        return False

    def insert_b2vinfo_commit(self, vtxid, vfromaddress, vtoaddress, vbamount, vvaddress, vsequence, vvamount, vvbtc, vcreateblock, vupdateblock, vstate):
        try:
            logger.debug("start insert_b2vinfo_commit")
            result = self.insert_b2vinfo(vtxid, vfromaddress, vtoaddress, vbamount, vvaddress, vsequence, vvamount, vvbtc, vcreateblock, vupdateblock, vstate)
            if result == False:
                return False
            self.__session.flush()
            return self.commit()
            
        except Exception as e:
            logger.error(traceback.format_exc(limit=self.__traceback_limit))
        return False

    def commit(self):
        try:
            logger.debug("start commit")
            self.__session.commit()
            return True
        except Exception as e:
            logger.error(traceback.format_exc(limit=self.__traceback_limit))
        return False

    def query_b2vinfo(self, vaddress, sequence):
        proofs = []
        try:
            logger.debug("start query_b2vinfo %s %i", vaddress, sequence)
            filter_vaddr = (self.b2vinfo.vaddress==vaddress)
            filter_seq = (self.b2vinfo.sequence==sequence)
            proofs = self.__session.query(self.b2vinfo).filter(filter_seq).filter(filter_vaddr).all()
            return proofs 
        except Exception as e:
            logger.error(traceback.format_exc(limit=self.__traceback_limit))
        return proofs 

    def __query_b2vinfo_state(self, state):
        proofs = []
        try:
            logger.debug("start query_b2vinfo state is %s ", state.name)
            filter_state = (self.b2vinfo.state==state.value)
            proofs = self.__session.query(self.b2vinfo).filter(filter_state).all()
            return proofs 
        except Exception as e:
            logger.error(traceback.format_exc(limit=self.__traceback_limit))
        return proofs 

    def query_b2vinfo_is_start(self):
        return self.__query_b2vinfo_state(self.state.START)

    def query_b2vinfo_is_succeed(self):
        return self.__query_b2vinfo_state(self.state.SUCCEED)

    def query_b2vinfo_is_failed(self):
        return self.__query_b2vinfo_state(self.state.FAILED)

    def update_b2vinfo(self, vaddress, sequence, state):
        try:
            logger.debug("start update_b2vinfo state to %s filter(vaddress, sequence) %s %i", state.name, vaddress, sequence)
            filter_vaddr = (self.b2vinfo.vaddress==vaddress)
            filter_seq = (self.b2vinfo.sequence==sequence)
            result = self.__session.query(self.b2vinfo).filter(filter_seq).filter(filter_vaddr).update({self.b2vinfo.state:state.value})
            return True
        except Exception as e:
            logger.error(traceback.format_exc(limit=self.__traceback_limit))
        return False

    def update_b2vinfo_to_succeed(self, vaddress, sequence, state):
        return self.update_b2vinfo(vaddress, sequence, self.state.SUCCEED)

    def update_b2vinfo_to_failed(self, vaddress, sequence, state):
        return self.pdate_b2vinfo(vaddress, sequence, self.state.FAILED)

    def __update_b2vinfo_commit(self, vaddress, sequence, state):
        try:
            logger.debug("start query_b2vinfo_commit")
            result = self.update_b2vinfo(vaddress, sequence, state)
            if result == False:
                return False

            return self.commit()
        except Exception as e:
            logger.error(traceback.format_exc(limit=self.__traceback_limit))
        return False

    def update_b2vinfo_to_start_commit(self, vaddress, sequence):
        return self.__update_b2vinfo_commit(vaddress, sequence, self.state.START)

    def update_b2vinfo_to_succeed_commit(self, vaddress, sequence):
        return self.__update_b2vinfo_commit(vaddress, sequence, self.state.SUCCEED)

    def update_b2vinfo_to_failed_commit(self, vaddress, sequence):
        return self.__update_b2vinfo_commit(vaddress, sequence, self.state.FAILED)


dbfile = "bve_b2v.db"
traceback_limit = setting.traceback_limit
def test_dbb2v_insert():
    b2v = dbb2v(dbfile, traceback_limit)
    b2v.insert_b2vinfo("0000000000000000000000000000000000000000000000000000000000000001", \
                "2NFMbhLACujsHKa45X4P2fZupVrgB268pbo", \
                "2NFMbhLACujsHKa45X4P2fZupVrgB268pbo", \
                1, \
                "c8b9311393966d5b64919d73c3d27d88f7f5744ff2fc288f0177761fe0671ca2", \
                2, #sequence 
                0, \
                "0000000000000000000000000000000000000000000000000000000000000000", \
                "e36d8ad4f1ab2ecbaf63d14ac150d464d81ef0fdf45ad0df8c27efaf8a10410d", \
                "e36d8ad4f1ab2ecbaf63d14ac150d464d81ef0fdf45ad0df8c27efaf8a10410d"
                )
    b2v.commit()

def test_dbb2v_query():
    try:
        logger.debug("*****************************************start test_dbb2v_query*****************************************")
        b2v = dbb2v(dbfile, traceback_limit)
        proofs = b2v.query_b2vinfo("c8b9311393966d5b64919d73c3d27d88f7f5744ff2fc288f0177761fe0671ca2", 2)

        if(len(proofs) == 0):
            logger.debug("not fount proof")

        for proof in proofs:
            logger.info("vaddress: %s" % (proof.vaddress))
            logger.info("sequence: %s" % (proof.sequence))
            logger.info("state : %i" % (proof.state))
    except Exception as e:
        logger.error(traceback.format_exc(limit=traceback_limit))

def test_dbb2v_query_state_start():
    try:
        logger.debug("*****************************************start test_dbb2v_query_state_start****************************")
        b2v = dbb2v(dbfile, traceback_limit)
        proofs = b2v.query_b2vinfo_is_start()

        if(len(proofs) == 0):
            logger.debug("not fount proof")

        for proof in proofs:
            logger.info("vaddress: %s" % (proof.vaddress))
            logger.info("sequence: %s" % (proof.sequence))
            logger.info("state : %i" % (proof.state))
    except Exception as e:
        logger.error(traceback.format_exc(limit=traceback_limit))

def test_dbb2v_query_state_succeed():
    try:
        logger.debug("*****************************************start test_dbb2v_query_state_succeed*************************")
        b2v = dbb2v(dbfile, traceback_limit)
        proofs = b2v.query_b2vinfo_is_succeed()

        if(len(proofs) == 0):
            logger.debug("not fount proof")

        for proof in proofs:
            logger.info("vaddress: %s" % (proof.vaddress))
            logger.info("sequence: %s" % (proof.sequence))
            logger.info("state : %i" % (proof.state))
    except Exception as e:
        logger.error(traceback.format_exc(limit=traceback_limit))

def test_dbb2v_query_state_failed():
    try:
        logger.debug("*****************************************start test_dbb2v_query_state_failed*************************")
        b2v = dbb2v(dbfile, traceback_limit)
        proofs = b2v.query_b2vinfo_is_failed()

        if(len(proofs) == 0):
            logger.debug("not fount proof")

        for proof in proofs:
            logger.info("vaddress: %s" % (proof.vaddress))
            logger.info("sequence: %s" % (proof.sequence))
            logger.info("state : %i" % (proof.state))
    except Exception as e:
        logger.error(traceback.format_exc(limit=traceback_limit))


def test_dbb2v_update():
    try:
        logger.debug("*****************************************start t_dbb2v_update***************************************")
        b2v = dbb2v(dbfile, traceback_limit)
        b2v.update_b2vinfo_to_succeed_commit("c8b9311393966d5b64919d73c3d27d88f7f5744ff2fc288f0177761fe0671ca2", 2)
    except Exception as e:
        logger.error(traceback.format_exc(limit=traceback_limit))

def test():
    try:
        test_dbb2v_insert()
        test_dbb2v_query()
        test_dbb2v_update()
        test_dbb2v_query()
        test_dbb2v_query_state_start()
        test_dbb2v_query_state_succeed()
        test_dbb2v_query_state_failed()
    except Exception as e:
        logger.error(traceback.format_exc(limit=traceback_limit))

if __name__ == "__main__" :
    test()
