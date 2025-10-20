from enum import Enum, auto
import threading
import time
import subprocess as sp
import codecs
import re
import os

from .debug import *
from .utils import getch, save_list, load_list

import traceback

class ArgParser:
    CMD_ARG_PREFIX = ""
    def __init__(self, args=None):
        self.__args_dict = None
        self.__target_keys = None

        # post init
        if args is not None:
            self.set_args(args)
    def __str__(self):
        print(self.__target_keys)
    def __getitem__(self, key):
        # dbg_debug("__getitem__")
        if self.__keytransform__(key) is None:
            # dbg_debug("Return None")
            return None
        else:
            return self.__args_dict[self.__keytransform__(key)]
    def __keytransform__(self, key):
        # dbg_debug("__keytransform__")
        if key not in self.keys():
            # dbg_debug("Return None")
            return None
        else:
            return key

    def set_args(self, args):
        # self.__args_dict = ArgParser.args_parser(args)
        if args is not None:
            self.__args_dict = ArgParser.args_parser(args)
        else:
            dbg_warning("No args data found.")
            self.__args_dict = dict()

    def keys(self):
        return self.__args_dict.keys()

    @property
    def target_keys_list(self):
        return self.__target_keys
    @target_keys_list.setter
    def target_keys_list(self,val):
        self.__target_keys = val

    @staticmethod
    def args_parser(args):
        """
        Parses a string of arguments into a dictionary.
        Arguments can be in the format 'key:value' or just 'value'.
        Positional arguments are stored with keys 'arg_0', 'arg_1', etc.
        A special key '#' stores the count of positional arguments.
        """

        # print (args)
        # def_key_prefix='arg_'
        def_key_prefix=ArgParser.CMD_ARG_PREFIX
        def_key_num_arg='#'
        def_key_all_arg='@'
        def_key_seperator='='
        def_key_idx=0
        # dbg_trace(args)
        arg_dict=dict()
        pattern = re.compile(r'''((?:[^\s"']|"[^"]*"|'[^']*')+)''')
        arg_list = []

        arg_cnt = -1

        for each_arg in pattern.split(args):
            if each_arg == '' or each_arg == " ":
                continue
            arg_list.append(each_arg)

            tmp_list=each_arg.split(def_key_seperator)

            if len(tmp_list) == 1:
                # add num:value
                arg_dict[def_key_prefix+def_key_idx.__str__()] = each_arg.replace("'", '').replace("\"", '')
                def_key_idx=def_key_idx+1
                arg_cnt += 1
            elif len(tmp_list) == 2:
                # add key:value
                arg_dict[tmp_list[0]] = tmp_list[1].replace("'", '').replace("\"", '')

        arg_dict[def_key_prefix+def_key_num_arg.__str__()] = arg_cnt
        arg_dict[def_key_prefix+def_key_all_arg.__str__()] = arg_list
        # print(arg_dict)
        return arg_dict

class CommandInstance:
    def __init__(self, key_word, func_ptr, description="", arg_list=None, group='default'):
        # key_word, func_ptr, description="", arg_list=l
        self.__key_word    = key_word
        self.__func_ptr    = func_ptr
        self.__description = description
        self.__arg_list    = arg_list
        self.__group       = group

    @property
    def key_word(self):
        return self.__key_word
    @key_word.setter
    def key_word(self,val):
        self.__key_word = val

    @property
    def func_ptr(self):
        return self.__func_ptr
    @func_ptr.setter
    def func_ptr(self,val):
        self.__func_ptr = val

    @property
    def description(self):
        return self.__description
    @description.setter
    def description(self,val):
        self.__description = val

    @property
    def arg_list(self):
        return self.__arg_list
    @arg_list.setter
    def arg_list(self,val):
        self.__arg_list = val

    @property
    def group(self):
        return self.__group
    @group.setter
    def group(self,val):
        self.__group = val

class CommandLineInterface:
    DEBUG_MODE = False
    def __init__(self, promote="cli", wellcome_message = "", on_exit = None):
        #### def vars ###
        self.__cmd_group_hidden="hidden"

        #### config vars ###
        self.__promote=promote + "> "
        self.__cmd_promote=promote + "$ "
        self.__one_command_keyword=":"
        self.__wellcome_message=wellcome_message

        #### control vars ###
        self.__flag_running = True
        # self.__flag_one_command = True
        self.__flag_one_command = False

        ### local vars ###
        self.__history_list = []
        self.__function_dict = dict()
        self.__auto_match = True
        self.__default_ptr = self.__default
        self.__mode = 0

        ### path vars ###
        self.__history_path = f"./.{promote}_history.log"

        ### Function Configs ###
        self.regist_cmd("lock", self.__lock, "Lock the command line.")
        self.regist_cmd("exit", self.__exit, "Exit the program")
        self.regist_cmd("help", self.__help, "Print help")
        self.regist_cmd("history", self.__hist, "Print history")
        self.regist_cmd("log", self.__log_level, "Setting log level. (all, disable, default.)", arg_list=["all", 'default', 'develoment', "disable", "critical", "error", "warning", "information", "debug", "trace", "max"])

        # debug mode.
        self.regist_cmd("debug", self.__set_debug_mode, "Set debug mode.(on, off)", arg_list=["on", "off"])
        self.regist_cmd("reg_table", self.__reg_table, "Dump registered command table.", group=self.__cmd_group_hidden)

    @staticmethod
    def vprint(*args, end="\n"):
        if CommandLineInterface.DEBUG_MODE is True:
            print("".join(map(str,args)), end=end, flush=True)
    @staticmethod
    def print(*args, end="\n"):
        print("".join(map(str,args)), end=end, flush=True)
    # @staticmethod
    # def println(*args):
    #     print("".join(map(str,args)), flush=True)
    def __cls(self):
        print('\x1bc')
    def __print_line_buffer(self, line_buffer, cursor_shift_idx):
        columns, rows = os.get_terminal_size(0)
        trailing_space_nmu=columns - len("\r"+self.__promote+line_buffer)

        # \033[ is csi
        if self.__mode == 1:
            print("\033[1K\r"+self.__cmd_promote+line_buffer+trailing_space_nmu*" ", end="", flush=True)
            print("\033[%dD" % (cursor_shift_idx + trailing_space_nmu), end="", flush=True)
        else:
            print("\033[1K\r"+self.__promote+line_buffer+trailing_space_nmu*" ", end="", flush=True)
            print("\033[%dD" % (cursor_shift_idx + trailing_space_nmu), end="", flush=True)

    @property
    def one_command(self):
        return self.__flag_one_command
    @one_command.setter
    def one_command(self,val):
        self.__flag_one_command = val

    @property
    def history_path(self):
        return self.__history_path
    @history_path.setter
    def history_path(self,val):
        self.__history_path = val

    def load_history(self):
        if self.__history_path is not None:
            self.__history_list = load_list(self.__history_path)
            dbg_trace(f"Load history from {self.__history_path}.")

    def save_history(self):
        if self.__history_path is not None:
            save_list(self.__history_list, self.__history_path)
            dbg_trace(f"Save history to {self.__history_path}.")

    def regist_cmd(self, key_word, func_ptr, description="", arg_list=None, group="default"):
        self.__function_dict[key_word] = CommandInstance(key_word=key_word, func_ptr=func_ptr, description=description, arg_list=arg_list, group=group)
    def regist_default_cmd(self, func_ptr):
        self.__default_ptr = func_ptr

    def run_once_def(self, line_args):
        func_ret = False
        if len(line_args) == 0:
            return True
        line_buffer=line_args

        arg_dict = ArgParser.args_parser(line_buffer)
        # get key only
        first_key = list(arg_dict.keys())[0]
        cmd_token = arg_dict[first_key]

        dbg_debug("Def Cmd: ", line_buffer)

        func_ret = self.__default_ptr(arg_dict)
        return func_ret
    def run_once_cmd(self, line_args):
        func_ret = False
        if len(line_args) == 0:
            dbg_debug("args is empty: ", line_args)
            return True
        line_buffer=line_args

        arg_dict = ArgParser.args_parser(line_buffer)
        # get key only
        first_key = list(arg_dict.keys())[0]
        cmd_token = arg_dict[first_key]

        dbg_debug("Cmd: ", line_buffer)
        for each_key in self.__function_dict.keys():
            if each_key == cmd_token or \
                    (self.__auto_match is True and len(cmd_token) >= 3 and len(each_key) >= len(cmd_token) and cmd_token == each_key[:len(cmd_token)]):
                try:
                    dbg_trace(f"Key:{{each_key}}, func_ptr: {self.__function_dict[each_key].func_ptr.__str__()}")
                    func_ret = self.__function_dict[each_key].func_ptr(arg_dict)
                except Exception as e:

                    dbg_error("Cmd: ", line_buffer)
                    dbg_error("Exception: ", e)

                    traceback_output = traceback.format_exc()
                    dbg_error(traceback_output)
                return func_ret

        dbg_error("Cmd not found. ", line_buffer)
        # func_ret = self.__default_ptr(arg_dict)
        return func_ret
    def run_once(self, line_args):
        dbg_error("Exception: ")
        func_ret = self.run_once_cmd(line_args)
        if func_ret is False:
            return self.run_once_def(line_args)

    def run(self):
        func_ret = None
        self.load_history()
        if self.__wellcome_message != "":
            self.print(self.__wellcome_message)

        self.on_enter()
        while self.__flag_running == True:
            try:
                line_buffer=self.get_line()

                # check ! and replace with history
                if len(line_buffer) >= 2 and line_buffer.startswith('!') and line_buffer[1:].isdigit():
                    hist_idx = int(line_buffer[1:])
                    if hist_idx <= len(self.__history_list):
                        line_buffer = self.__history_list[hist_idx]

                cmd_token=line_buffer.split(' ')

                if self.__mode == 1:
                    # if cmd_token[0][0] == self.__one_command_keyword:
                    if len(line_buffer) != 0:
                        dbg_info('One Command Mode')
                        func_ret = self.run_once_cmd(line_buffer)
                    else:
                        # dbg_debug('line_buffer->' , line_buffer)
                        func_ret = self.run_once_def(line_buffer)
                else:
                    if self.__flag_one_command is True:
                        func_ret = self.run_once_def(line_buffer)
                    else:
                        func_ret = self.run_once_cmd(line_buffer)

                if func_ret is not True:
                    self.print('Fail to excute command. Return:', func_ret)
            except Exception as e:
                dbg_error("Cmd: ", line_buffer)
                dbg_error("Exception: ", e)

                traceback_output = traceback.format_exc()
                dbg_error(traceback_output)
        self.save_history()

    def __auto_complete(self, line_buffer):
        candict_list = list()
        # print('\n__auto_complete')
        cmd_token = line_buffer.split(' ')
        if len(cmd_token) == 1 and cmd_token[0] != '':
            # print('auto compolete cmd', cmd_token, cmd_token[0])
            pattern = cmd_token[0]
            arg_list = self.__function_dict.keys()
            for each_key in arg_list:
                if each_key.startswith(pattern) is True:
                    # print(each_key)
                    candict_list.append(each_key)
        elif len(cmd_token) > 1:
            # print('auto compolete args', cmd_token, cmd_token[0], cmd_token[-1])
            pattern = cmd_token[-1]
            command = cmd_token[0]
            if command in self.__function_dict.keys() and self.__function_dict[command].arg_list is not None:
                arg_list = self.__function_dict[command].arg_list
            else:
                arg_list = list()
            # print('arg_list',arg_list)
            if line_buffer.endswith(' ') is True:
                candict_list = arg_list
            else:
                for each_key in arg_list:
                    if each_key.startswith(pattern) is True:
                        # print(each_key)
                        candict_list.append(each_key)
        elif len(cmd_token) == 1 and cmd_token[0] == '':
            candict_list = list(self.__function_dict.keys())
        # else:
        #     print('No need to complete')

        # print(candict_list)
        return candict_list

    def get_line(self):
        self.__mode=0
        ckey_timestatmp=time.time()
        pkey_timestatmp=time.time()
        key_timeout=50.0

        line_buffer=""
        line_bakup_buffer=""
        esc_dectect=False
        pkey_press=""
        skip_nkey=0
        history_idx=0
        buffer_cusor_idx=0

        print("\r"+self.__promote+line_buffer, end='', flush=True)
        while self.__flag_running == True:
            pkey_timestatmp = ckey_timestatmp
            # key_press = getch()
            try:
                key_press = getch()
            except KeyboardInterrupt:
                key_press = chr(0x03)
            except Exception as e:
                dbg_error(e)
            
                traceback_output = traceback.format_exc()
                dbg_error(traceback_output)
                raise e
            ckey_timestatmp=time.time()

            # for skip following keys
            if skip_nkey > 0 and ckey_timestatmp - pkey_timestatmp < key_timeout:
                # dbg_debug("skip following keys")
                skip_nkey = skip_nkey - 1
                continue

            ## For future dev
            # print("\nKey Code: ", key_press.encode("ascii"))

            # special key press
            if key_press == chr(0x1b):
                # esc
                if esc_dectect is True:
                    dbg_trace("Double Esc Key")
                    esc_dectect=False
                    self.__mode = 0
                else:
                    esc_dectect=True
                # dbg_debug("Esc Key")
                continue
            elif key_press == chr(0x04):
                # ctrl + d
                line_buffer=""
                self.__exit(None)
                break
            elif key_press == chr(0x0c):
                # ctrl + l
                self.__cls()
                self.__print_line_buffer(line_buffer, buffer_cusor_idx)
                continue
            elif key_press == chr(0x03):
                # ctrl + c
                line_buffer=""
                line_bakup_buffer=""
                esc_dectect=False
                pkey_press=""
                history_idx=0
                buffer_cusor_idx=0
                print('^c')
                self.__print_line_buffer(line_buffer, buffer_cusor_idx)
                continue
            elif key_press == chr(0x7f):
                # backspace
                # print("test")
                # print("info", len(line_buffer), buffer_cusor_idx)
                if len(line_buffer) > buffer_cusor_idx:
                    tmp_idx=len(line_buffer)-(buffer_cusor_idx + 1)
                    line_buffer = line_buffer[:tmp_idx] + line_buffer[tmp_idx + 1:]
                # else:
                #     tmp_idx=len(line_buffer)-(buffer_cusor_idx + 1)


                # self.print('')
                # self.print("Start: " + line_buffer[:tmp_idx])
                # self.print("End: " + line_buffer[tmp_idx:] )
                self.__print_line_buffer(line_buffer, buffer_cusor_idx)
                continue
            elif key_press == chr(0x09):
                # print('\n'+line_buffer+'\n')
                # candict_list = self.__auto_complete(line_buffer)
                center_idx = len(line_buffer) - buffer_cusor_idx
                front_buffer = line_buffer[:center_idx]
                post_buffer = line_buffer[center_idx:]
                # print('\n'+ 'cmd ->' + front_buffer + ' - ' + post_buffer + '\n')

                candict_list = self.__auto_complete(front_buffer)
                # print(candict_list)
                if len(candict_list) == 1:
                    last_arg = front_buffer.split(' ')[-1]
                    line_buffer = front_buffer + candict_list[0][len(last_arg):] + post_buffer
                    # print('\n',candict_list)
                elif len(candict_list) > 1:
                    print('\n', candict_list)

                self.__print_line_buffer(line_buffer, buffer_cusor_idx)
                continue
            # elif key_press.encode("ascii") == b':':
            elif key_press == ':':
                # dbg_info(': Dectect')
                self.__mode = 1
                self.__print_line_buffer(line_buffer, buffer_cusor_idx)
                continue
            # elif key_press.encode("ascii") == b'\x1f':

            if ckey_timestatmp - pkey_timestatmp < key_timeout and esc_dectect is True:
                if key_press == '[':
                    pkey_press = key_press
                    continue
                elif pkey_press == '[':
                    if key_press == 'D':
                        # return('left')
                        # self.print("Cursor Idx: ",buffer_cusor_idx)
                        if len(line_buffer) >= buffer_cusor_idx + 1:
                            buffer_cusor_idx=buffer_cusor_idx + 1
                            self.__print_line_buffer(line_buffer, buffer_cusor_idx)
                    elif key_press == 'C':
                        # return('right')
                        # self.print("Cursor Idx: ",buffer_cusor_idx)
                        if 1 <= buffer_cusor_idx:
                            buffer_cusor_idx=buffer_cusor_idx - 1
                            self.__print_line_buffer(line_buffer, buffer_cusor_idx)
                    elif key_press == 'A':
                        # self.print("Hist Idx: ",history_idx)
                        # return('up')
                        if 0 == history_idx:
                            line_bakup_buffer = line_buffer
                        if len(self.__history_list)  > history_idx:
                            history_idx=history_idx + 1
                            buffer_cusor_idx = 0
                            line_buffer=self.__history_list[-history_idx]
                        self.__print_line_buffer(line_buffer, buffer_cusor_idx)
                    elif key_press == 'B':
                        # self.print("Hist Idx: ",history_idx)
                        # return('down')
                        if 1 < history_idx:
                            history_idx=history_idx - 1
                            buffer_cusor_idx = 0
                            line_buffer=self.__history_list[-history_idx]
                        elif 1 == history_idx:
                            history_idx=history_idx - 1
                            line_buffer = line_bakup_buffer
                        self.__print_line_buffer(line_buffer, buffer_cusor_idx)
                    elif key_press == '3':
                        # FIXME This is not real key, only detect first 3 code
                        # Del
                        # print("Del Key")
                        skip_nkey = 1
                        if buffer_cusor_idx > 0:
                            tmp_idx=len(line_buffer)-(buffer_cusor_idx)
                            line_buffer = line_buffer[:tmp_idx] + line_buffer[tmp_idx + 1:]
                            buffer_cusor_idx = buffer_cusor_idx - 1

                        # self.print('')
                        # self.print("Start: " + line_buffer[:tmp_idx])
                        # self.print("End: " + line_buffer[tmp_idx:] )
                        self.__print_line_buffer(line_buffer, buffer_cusor_idx)
                    elif key_press == '1':
                        # FIXME This is not real key, only detect first 3 code
                        # Home
                        # print("Home Key")
                        skip_nkey = 1
                        buffer_cusor_idx = len(line_buffer)
                        self.__print_line_buffer(line_buffer, buffer_cusor_idx)
                    elif key_press == '4':
                        # FIXME This is not real key, only detect first 3 code
                        # End
                        # print("End Key")
                        skip_nkey = 1
                        buffer_cusor_idx = 0
                        self.__print_line_buffer(line_buffer, buffer_cusor_idx)

                esc_dectect=False
                pkey_press=''
                continue
            else:
                # print("Single ESC")
                esc_dectect=False
                pkey_press=''

            # normal key press
            if key_press in ("\r", "\n"):
                # print("Enter")
                print("\n", end='', flush=True)
                # self.__mode = 0
                break
            else:
                # update buffer
                tmp_idx=len(line_buffer)-(buffer_cusor_idx)
                line_buffer = line_buffer[:tmp_idx] + key_press + line_buffer[tmp_idx:]

                # update console
                self.__print_line_buffer(line_buffer, buffer_cusor_idx)
                continue
        # save only when it's not empty
        if line_buffer != "":
            self.__history_list.append(line_buffer)
        # self.print(self.__history_list)
        dbg_debug('line_buffer-'+line_buffer+'-')
        return line_buffer
    def __lock(self, args):
        dbg_info('Command line locked.')
        lock_password = '00112233'
        if args['#'] == 1:
            lock_password = args['1']
        enter_buffer = ''
        while True:
            try:
                enter_buffer = input("[Locked] Enter unlock key$ ")

                if len(enter_buffer) >= len(lock_password) and enter_buffer[-8:] == lock_password:
                    break
            except KeyboardInterrupt:
                print("")
                continue
            except Exception as e:
                print(e)
            
                traceback_output = traceback.format_exc()
                print(traceback_output)

        return True
    def __lock_bak(self, args):
        dbg_info('Command line locked.')
        lock_password = '00112233'
        if args['#'] == 1:
            lock_password = args['1']
        enter_buffer = ''
        while True:
            if enter_buffer != '':
                dbg_info(f'Enter Password: "{enter_buffer}"')
            key_press = getch()
            enter_buffer = enter_buffer[-7:] + key_press

            if len(enter_buffer) >= len(lock_password) and enter_buffer[-8:] == lock_password:
                break

        return True
    def __log_level(self, args):
        if args['#'] == 1:
            DebugSetting.setDbgLevel(args['1'])
            DebugSetting.dbg_show()
        return True
    def __set_debug_mode(self, args):
        if args['#'] == 1:
            if args['1'] == 'on':
                CommandLineInterface.DEBUG_MODE = True
                self.vprint("debug mode enabled.")
                return True
            elif args['1'] == 'off':
                CommandLineInterface.DEBUG_MODE = False
                return True
        return False

    def __default(self, args):
        self.print("Default Function")
        return True

    def on_enter(self):
        pass
    def on_exit(self):
        self.print("Exit program")

    def __exit(self, args):
        try:
            self.on_exit()
        except Exception as e:
            print(e)
        
            traceback_output = traceback.format_exc()
            print(traceback_output)
        self.__flag_running = False
        return True
    def __hist(self, args):
        self.print("History")
        for each_idx in range(0, len(self.__history_list)):
            self.print("% 4d. %s" % (each_idx,  self.__history_list[each_idx]))
        return True

    def __help(self, args):
        self.print("Help")
        max_len = 8
        default_group = 'default'
        group_list = [default_group]
        for each_key in self.__function_dict.keys():
            if len(each_key) + 2 > max_len:
                max_len = len(each_key) + 2

            if self.__function_dict[each_key].group not in group_list:
                group_list.append(self.__function_dict[each_key].group)

        for each_group in group_list:
            # hide hidden group if not in debug mode.
            if each_group == self.__cmd_group_hidden and not self.DEBUG_MODE:
                continue

            # don't print default group name.
            if each_group != default_group:
                self.print("[%s]" % (each_group))

            # print commands.
            for each_key in self.__function_dict.keys():
                if self.__function_dict[each_key].group == each_group:
                    self.print(f"  %- {max_len}s: %s" % (each_key, self.__function_dict[each_key].description))
        return True

    def __reg_table(self, args):
        self.print("Register Table:")
        max_len = 8
        for each_key in self.__function_dict.keys():
            if len(each_key) + 2 > max_len:
                max_len = len(each_key) + 2

        for each_key in self.__function_dict.keys():
            self.print(f"  %- {max_len}s: %s" % (each_key, self.__function_dict[each_key].func_ptr.__str__()))
        return True

def args_test_function(args):
    CommandLineInterface.print(f"cmd: {args['0']}, nargs:{args['#']}")
    for each_arg in range(1, args['#'] + 1):
        CommandLineInterface.print(f"arg {each_arg}: {args[each_arg.__str__()]}")
    return True

if __name__ == '__main__':

    debug_level=DebugLevel.MAX
    test_cli = CommandLineInterface()
    test_cli.regist_cmd("test", args_test_function, description="test function for args", arg_list=['project', 'task', 'name', 'description']  )
    test_cli.run()
