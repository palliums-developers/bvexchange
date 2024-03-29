#!/usr/bin/python3
import operator
import sys
import json
import os
import time
import requests
import getopt
import readline
import signal
sys.path.append(os.getcwd())
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))


import stmanage
import log
import log.logger
from comm.parseargs import parseargs
from comm.functions import json_print
from lbcommunication import (
        comm_client as client,
        )

def __run_with_cmd(name, client):
    while True:
        cmd = input(f"client.{name}$: ")
        state, cmd, args = parse_cmd(cmd)
        if state:
            if cmd in ("exit"):
                return

            argv = [cmd] + args
            try:
                client.run(len(argv), argv, exit = False)
            except Exception as e:
                print(e)
                pass
        else:
            try:
                argv = ["--help"]
                client.run(len(argv), argv, exit = False)
            except Exception as e:
                print(e)
                pass

def __use_module(name, client):
    try:
        show_module_info(name)
        client.chain = name
        __run_with_cmd(name, client)

    except Exception as e:
        print(e)
        pass

def __md_comm():
    import commtools
    __use_module("comm", commtools)

def __md_violas():
    from vlsopt import violastools
    __use_module("violas", violastools)

def __md_libra():
    from vlsopt import violastools
    __use_module("libra", violastools)

def __md_diem():
    from vlsopt import violastools
    __use_module("diem", violastools)

def __md_ethereum():
    from ethopt import ethtools
    __use_module("ethereum", ethtools)

def __md_cleanproof():
    from tools import clean_proof
    __use_module("cleanproof", clean_proof)
    
def __md_cleanlocaldbs():
    from tools import clean_localdbs
    __use_module("cleanlocaldbs", clean_localdbs)

def __md_initworkenv():
    from tools import init_workenv
    __use_module("initworkenv", init_workenv)

def __md_dbtools():
    from db import dbtools
    __use_module("dbtools", dbtools)

def use(module = None):
    START_SYMBOL = "__md_"
    support_module = [key[len(START_SYMBOL):] for key in globals() if key.startswith(START_SYMBOL)]
    if not module:
        return support_module
    if module not in support_module:
        print(f"module must be only one of {support_module}")

    globals()[f"{START_SYMBOL}{module}"]()

def init_args(pargs):
    pargs.clear()
    pargs.append("help", "show arg list.")
    pargs.append("conf", "config file path name. default:bvexchange.toml, find from . and /etc/bridge/", True, "toml file", priority = 5)
    pargs.append(use, "select module")

def show_module_info(module):
    print(f"switch to {module}")


def exit():
    sys.exit()

def process_args():
    pargs = parseargs(exit = False)
    pargs.append("help", "show arg list.")
    pargs.append(use, f"select module, args: {use()}")
    pargs.append(exit, f"exit client")

    return pargs

def help(pargs, args = None):
    if args is None or len(args) == 0:
        pargs.show_args()
    else:
        pargs.show_help(["help", args[0]])

def parse_cmd(cmd):
    cmd = cmd
    args = None
    state = True
    try:
        if not cmd:
            return (True, "help", [])

        cmd_arg = cmd.split(' ')
        cmd = cmd_arg[0]
        args = cmd_arg[1:]
        print(f"cmd = {cmd} args = {args}")
    except Exception as e:
        state = False
        pass


    return (state, cmd, args)

def process():
    pargs = process_args()
    while True:
        try:
            cmd = input("client$: ")
            state, cmd, args = parse_cmd(cmd)
            if state:
                if cmd == "help":
                    help(pargs, args)
                    continue
                if pargs.has_callback(cmd):
                    pargs.callback(cmd, *args)
        except Exception as e:
            print(e)
            pass

def main(argc, argv):
    try:
        init_signal()
        pargs = parseargs()
        init_args(pargs)
        opts, err_args = pargs.getopt(argv)
    except getopt.GetoptError as e:
        print(e)
        sys.exit(2)
    except Exception as e:
        print(e)
        sys.exit(2)

    #argument start for --
    if len(err_args) > 0:
        pargs.show_args()

    names = [opt for opt, arg in opts]
    pargs.check_unique(names)
    
    for opt, arg in opts:

        arg_list = []
        if len(arg) > 0:
            count, arg_list = pargs.split_arg(opt, arg)

            print("opt = {}, arg = {}".format(opt, arg_list))
        if pargs.is_matched(opt, ["help"]):
            pargs.show_args()
        elif pargs.is_matched(opt, ["conf"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            stmanage.set_conf_env(arg_list[0])

    process()


    logger.debug("end manage.main")

def init_signal():
    signal.signal(signal.SIGINT, signal_stop)
    signal.signal(signal.SIGTSTP, signal_stop)
    signal.signal(signal.SIGTERM, signal_stop)

def signal_stop(signal, frame):
    try:
        sys.exit(2)
    except Exception as e:
        parse_except(e)
    finally:
        print("closed")

if __name__ == "__main__":
    main(len(sys.argv) - 1, sys.argv[1:])

