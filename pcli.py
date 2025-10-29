
import time
import traceback
import sys
import io
import os # Import os module to get terminal size

from .debug import *
from .cli import CommandLineInterface
from .utils import getch, save_list, load_list

class PageShareData:
    def __init__(self):
        pass

class KeyInstance:
    def __init__(self, key_list, func_ptr, description="", group='default'):
        self.__key_list    = key_list
        self.__func_ptr    = func_ptr
        self.__description = description
        self.__group       = group

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

    @property
    def group(self):
        return self.__group
    @group.setter
    def group(self,val):
        self.__group = val

class PageCommandLineInterface:

    def __init__(self, share_data = None, title = "Page Command Line Interface", wellcome_message = "", on_exit = None):
        #### def vars ###
        self.__cmd_group_hidden="hidden"

        #### config vars ###
        self.__wellcome_message=wellcome_message
        self.__title = title

        #### control vars ###
        self.__flag_running = True
        self.__key_delay = 0.01
        self.__flag_show_help = False

        ### local vars ###
        self.__function_key_list = list()
        self.__content_handler_ptr = self.def_content_handler
        self.__content_offset = 0 # New: Offset for content display
        self.__title_handler_ptr = self.def_title_handler
        self.__status_handler_ptr = self.def_status_handler

        ### buffers ###
        self.share_data = share_data
        self.command_buffer = ""
        self.key_press_buffer = ""
        self.content_output_buffer = wellcome_message

        ### instance ###
        self.command_line = CommandLineInterface(promote = "cmd")
        self.command_line.set_prompt(prompt = ":", cmd_prompt = "$")

        ### Function Configs ###
        # self.regist_key(["q"], self.exit, "Exit the program")
        self.regist_key(["?"], self.key_help, "Toggle help display; press '?' again to hide it.")
        self.regist_key([":"], self.key_cmd, "Toggle command mode display; press again to hide it.")
        self.regist_key(["j","k"], self.key_move_ud, "Move content up/down")

    @staticmethod
    def vprint(*args, end="\n"):
        if CommandLineInterface.DEBUG_MODE is True:
            print("".join(map(str,args)), end=end, flush=True)
    @staticmethod
    def print(*args, end="\n"):
        print("".join(map(str,args)), end=end, flush=True)
    def cls(self):
        print('\x1bc')
    def set_cursor_visibility(self, visible):
        if visible:
            self.print("\033[?25h", end="")  # Show cursor
        else:
            self.print("\033[?25l", end="")  # Hide cursor
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

    ## Regs functons
    ##########################
    def regist_key(self, key_list, func_ptr, description="", group="default"):
        self.__function_key_list.append( KeyInstance(key_list=key_list, func_ptr=func_ptr, description=description, group=group) )

    def regist_cmd(self, key_word, func_ptr, description="", arg_list=None, group="default"):
        self.command_line.regist_cmd(key_word, func_ptr, description, group=group)

    def regist_content_handler(self, func_ptr):
        self.__content_handler_ptr = func_ptr

    def regist_title_handler(self, func_ptr):
        self.__title_handler_ptr = func_ptr

    def regist_status_handler(self, func_ptr):
        self.__status_handler_ptr = func_ptr

    ## UI Generation.
    ##########################
    def __ui_title_handler(self):
        # self.print('\x1bc', end='')
        self.print(f"\033[1;1H", end="")
        title = self.__title_handler_ptr(self.share_data)
        self.print("{}".format(title), end='')

    def __ui_status_handler(self):
        # Save current cursor position
        self.print("\033[s", end="")

        # Get terminal size
        columns, rows = os.get_terminal_size()
        # Move cursor to the last line
        self.print(f"\033[{rows - 1 };1H", end="")
        # self.print("Enter a key(q Exit, : command mode, ? Toggle help):")

        status_left, status_right = self.__status_handler_ptr()
        # Calculate padding for right alignment
        padding = columns - len(status_left) - len(status_right)
        # Print status_left, then padding spaces, then status_right
        self.print(f"{status_left}{' ' * padding}{status_right}", end="")

        # Restore cursor position
        self.print("\033[u", end="")

    def __ui_page_render(self):
        # columns, rows = os.get_terminal_size()
        columns, rows = os.get_terminal_size()
        # Calculate display height: total rows - 1 (title) - 1 (status) - 1 (command), leave 1 line before commands.
        display_height = rows - 3 - 1

        content_lines = self.content_output_buffer.splitlines()
        total_content_lines = len(content_lines)

        # Adjust offset if it goes out of bounds
        if self.__content_offset < 0:
            self.__content_offset = 0
        if self.__content_offset > total_content_lines - display_height:
            self.__content_offset = max(0, total_content_lines - display_height)

        # Move cursor to the start of the content area (line 2)
        self.print(f"\033[2;1H", end="")

        # Print content from the offset
        for i in range(display_height):
            line_idx = self.__content_offset + i
            if line_idx < total_content_lines:
                # Clear the current line and print new content
                self.print(f"\033[K{content_lines[line_idx]}")
            else:
                # Clear the line if there's no more content to fill the display height
                self.print("\033[K")

    def __ui_page_handler(self):
        # Redirect stdout to a buffer
        old_stdout = sys.stdout
        redirect_buffer = io.StringIO()
        sys.stdout = redirect_buffer

        ## Content
        if self.__flag_show_help:
            self.page_help()
            # self.__flag_show_help = False
        else:
            self.__content_handler_ptr()

        # Restore stdout and capture the output
        sys.stdout = old_stdout
        self.content_output_buffer = redirect_buffer.getvalue()
        self.__ui_page_render()

    def __ui_command_handler(self):
        # Save current cursor position
        self.print("\033[s", end="")

        # Get terminal size
        columns, rows = os.get_terminal_size()
        # Move cursor to the last line
        self.print(f"\033[{rows};1H", end="")

        if len(self.command_buffer) != 0:
            self.print(f"{self.command_buffer}", end = "")
            self.command_buffer = f""

        # Restore cursor position
        self.print("\033[u", end="")
    def run(self):
        while True:
            try:
                # reset terminal and cls
                self.cls()
                self.set_cursor_visibility(False)

                self.__ui_title_handler()
                self.__ui_page_handler()
                self.__ui_status_handler()
                self.__ui_command_handler()

                self.share_data.flag_redraw = False

                # reset variables
                self.key_press_buffer = ""
                need_redraw = False
                while not need_redraw:

                    key_press = getch()
                    time.sleep(self.__key_delay)

                    if key_press in ("q") or key_press == chr(0x04):
                        # ctrl + d
                        self.cls()
                        self.exit(data = self.share_data)
                        self.set_cursor_visibility(True)
                        return True
                    elif key_press in ("r") or key_press == chr(0x0c):
                        # ctrl + l and refresh
                        self.refresh(data = self.share_data)
                        need_redraw = True
                        break
                    else:
                        try:
                            for each_func in self.__function_key_list:
                                if key_press in each_func.key_list:
                                    need_redraw = each_func.func_ptr(key_press = key_press, data = self.share_data)

                                    # update status bar.
                                    self.__ui_status_handler()
                                    continue
                        except Exception as e:
                            self.print(e)

                            traceback_output = traceback.format_exc()
                            self.print(traceback_output)
                # record key_press.
                self.key_press_buffer = key_press
            except Exception as e:
                dbg_error(e)

                traceback_output = traceback.format_exc()
                dbg_error(traceback_output)
            # finally:
            #     pass
        self.set_cursor_visibility(True)
        return True

    ## Build-in functions
    ##########################
    def refresh(self, data = None):
        return True
    def exit(self, data = None):
        return True

    # default handler
    def def_content_handler(self, data = None):
        self.print("|| {} ||".format("Default content handler."))
        return True

    def def_title_handler(self, data = None):
        title = "== {} ==".format(self.__title)
        return title

    def def_status_handler(self, data = None):
        status_left = "q Exit, : command mode, ? Toggle help"
        status_right = ""
        # tupple (left, right)
        return (status_left,status_right)

    ## Page
    def page_help(self, data = None):
        self.print("Help:")
        for each_func in self.__function_key_list:
            self.print(f"  {str(each_func.key_list):<16}: {each_func.description}")
        self.print(f"  {str(['q']):<16}: Quit.")
        return True

    ## key & command
    def key_help(self, key_press, data = None):
        self.__flag_show_help = not self.__flag_show_help
        return True

    def key_cmd(self, key_press, data = None):
        # Save current cursor position
        self.print("\033[s", end="")
        self.set_cursor_visibility(True)

        # Get terminal size
        columns, rows = os.get_terminal_size()
        # Move cursor to the last line
        self.print(f"\033[{rows};1H", end="")

        # Clear the reset of the line.
        self.print("\033[K", end="")

        # self.command_buffer = input(":")
        func_ret = self.command_line.run_once()
        if func_ret is False:
            self.command_buffer = f"Execute return fail. {func_ret}"

        # Restore cursor position
        self.print("\033[u", end="")
        self.set_cursor_visibility(False)

        return True
    def key_move_ud(self, key_press, data = None):
        columns, rows = os.get_terminal_size()
        display_height = rows - 3
        total_content_lines = len(self.content_output_buffer.splitlines())

        # Calculate the maximum allowed offset
        # If content fits on screen, max_offset is 0. Otherwise, it's total_lines - display_height.
        max_offset = max(0, total_content_lines - display_height)

        if key_press == 'j':
            if self.__content_offset < max_offset:
                self.__content_offset += 1
        elif key_press == 'k':
            self.__content_offset -= 1
            if self.__content_offset < 0:
                self.__content_offset = 0
        return True

    ##########################

if __name__ == "__main__":
    share_data = PageShareData

    test_pcli = PageCommandLineInterface(share_data = share_data)
    test_pcli.run()
