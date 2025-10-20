
import time
import traceback

from .debug import *
from .utils import getch, save_list, load_list

class KeyInstance:
    def __init__(self, key_list, func_ptr, description="", arg_list=None, group='default'):
        # key_list, func_ptr, description="", arg_list=l
        self.__key_list    = key_list
        self.__func_ptr    = func_ptr
        self.__description = description
        # self.__arg_list    = arg_list
        # self.__group       = group

    @property
    def key_list(self):
        return self.__key_list
    @key_list.setter
    def key_list(self,val):
        self.__key_list = val

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

    # @property
    # def arg_list(self):
    #     return self.__arg_list
    # @arg_list.setter
    # def arg_list(self,val):
    #     self.__arg_list = val

    # @property
    # def group(self):
    #     return self.__group
    # @group.setter
    # def group(self,val):
    #     self.__group = val

class PageCommandLineInterface:

    def __init__(self, title = "Page Command Line Interface",wellcome_message = "", on_exit = None):
        #### def vars ###
        self.__cmd_group_hidden="hidden"

        #### config vars ###
        self.__wellcome_message=wellcome_message
        self.__title = title

        #### control vars ###
        self.__flag_running = True
        self.__key_delay = 0.01

        ### local vars ###
        self.__function_list = list()

        ### Function Configs ###
        # self.regist_key(["q"], self.__exit, "Exit the program")
        self.regist_key(["?"], self.__help, "Print help")

    def __help(self, data = None):
        self.print("Help:")
        for each_func in self.__function_list:
            self.print(f"  {str(each_func.key_list):<16}: {each_func.description}")
        self.print(f"  {str(['q']):<16}: Quit.")
        return True

    def __exit(self, data = None):
        return True

    def __ui_print_title(self, title):
        self.print('\x1bc')
        self.print("== {} ==".format(title))
    def __ui_short_key_help(self):
        # Save current cursor position
        self.print("\033[s", end="")

        # Get terminal size
        columns, rows = os.get_terminal_size()
        # Move cursor to the last line
        self.print(f"\033[{rows};1H", end="")
        self.print("Enter a key(q:Exit, j:Next, k:Previous, f:Familiar, n:New words, 0-5:Grade, ::Search):")
        # Restore cursor position
        self.print("\033[u", end="")

    @staticmethod
    def vprint(*args, end="\n"):
        if CommandLineInterface.DEBUG_MODE is True:
            print("".join(map(str,args)), end=end, flush=True)
    @staticmethod
    def print(*args, end="\n"):
        print("".join(map(str,args)), end=end, flush=True)
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

    def regist_key(self, key_list, func_ptr, description="", arg_list=None, group="default"):
        self.__function_list.append( KeyInstance(key_list=key_list, func_ptr=func_ptr, description=description, arg_list=arg_list, group=group) )
    def run_list(self, page_list):
        word_idx = 0
        page_list = [1, 2, 3, 4, 5]
        while True:
            if word_idx > len(page_list) - 1:
                word_idx = len(page_list) - 1
            elif word_idx == -1:
                word_idx = 0

            # cls
            self.__cls()
            self.print("== Listing words. ==")
            self.print("Enter a key(q:Exit, j:Next, k:Previous, f:Familiar, n:New words, 0-5:Grade, ::Search):")
            while True:

                key_press = getch()
                time.sleep(self.__key_delay)

                if key_press in ("j"):
                    word_idx += 1
                    break
                elif key_press in ("k"):
                    word_idx -= 1
                    break
                elif key_press in ("q", "Q") or key_press == chr(0x04):
                    # ctrl + d
                    return True
                elif key_press == chr(0x0c):
                    # ctrl + l
                    break
                else:
                    print("Unknown key>" + key_press)
                    continue
    def run(self, data):
        while True:

            # cls
            self.__cls()
            self.__ui_print_title(self.__title)
            # change to short help
            # self.__ui_short_key_help()

            while True:

                key_press = getch()
                time.sleep(self.__key_delay)

                if key_press in ("q") or key_press == chr(0x04):
                    # ctrl + d
                    self.__cls()
                    self.__exit()
                    return True
                elif key_press == chr(0x0c):
                    # ctrl + l
                    break

                try:
                    for each_func in self.__function_list:
                        if key_press in each_func.key_list:
                            each_func.func_ptr(data = data)
                except Exception as e:
                    self.print(e)

                    traceback_output = traceback.format_exc()
                    self.print(traceback_output)
        return True

if __name__ == "__main__":

    test_pcli = PageCommandLineInterface()
    test_pcli.run()
