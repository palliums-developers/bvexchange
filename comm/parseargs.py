#!/usr/bin/python3
import operator
import sys, getopt
import json
sys.path.append("..")
import log
import log.logger
import traceback
import datetime
#from .models import BtcRpc
from enum import Enum

#module name
name="btcclient"

#load logging
logger = log.logger.getLogger(name) 

class parseargs:
    __args = {}
    __unique = []

    def __init__(self):
        pass

    def __del__(self):
        pass

    def appendunique(self, opts_unique):
        if opts_unique is None:
            return
        self.__unique.append(list(opts_unique))

    def check_unique(self, opts):
        pass
        opt_list = [name.replace("--", "") for name in opts]
        for uni in self.__unique:
            count = 0
            for opt in opt_list:
                if opt in uni:
                    count += 1
                if count > 1:
                    print(f"found Mutually exclusive parameters ({uni})")
                    sys.exit(2)



    def append(self, name, desc, hasarg = False, arglist = None):
        if name in self.__args:
            raise Exception("arg is exists.")
        if hasarg:
            key = f"{name}-"
            value = f"desc: {desc} format: --{name} \"{arglist}\""
        else:
            key = name
            value = f"desc: {desc} format: --{name}"
        self.__args[key] = value

    def remove(self, name):
        if self.__args is None or name not in self.__args:
            return
        del self.__args[name]

    def show_args(self):
        for key in list(self.__args.keys()):
            print("{}{} \n\t\t\t\t{}".format("--", key.replace('-', ''), self.__args[key].replace('\n', '')))
        sys.exit(2)

    def exit_error_opt(self, opt):
        print(self.__args["{}-".format(opt.replace('--', ''))])
        sys.exit(2)

    def __show_arg_info(self, info):
        print(info)


    def list_arg_name(self):
        return [ "--" + arg.replace('-', "") for arg in self.args.keys()]

    def show_help(self, args):
        if args is None or len(args) != 2 or args[0] != "help" :
            return
        name = args[1]

        if name in self.__args:
            self.__show_arg_info("--{} \n\t{}".format(name, self.__args[name].replace("format:", "\n\tformat:")))
        else:
            self.__show_arg_info("--{} \n\t{}".format(name, self.__args["{}-".format(name)].replace("format:", "\n\tformat:")))
        system.exit(2)

    def getopt(self, argv):
        return getopt.getopt(argv, None, [arg.replace('-', "=") for arg in self.__args.keys()])

    def is_matched(self, opt, names):
        nl = [ "--" + name for name in names]
        return opt in nl

    def split_arg(self, arg, sign = ','):
        if arg is None:
            return (0, None)
        arg_list = "{}".format(arg).split(sign)
        return  (len(arg_list), [sub.strip() for sub in arg_list])