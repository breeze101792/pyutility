from time import gmtime, strftime
# import threading
import inspect
import os

# black        0;30     Dark Gray     1;30
# Red          0;31     Light Red     1;31
# Green        0;32     Light Green   1;32
# Brown/Orange 0;33     Yellow        1;33
# Blue         0;34     Light Blue    1;34
# Purple       0;35     Light Purple  1;35
# Cyan         0;36     Light Cyan    1;36
# Light Gray   0;37     White         1;37
class Bcolors:
    TRACE = '\033[37m'
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    CRITICAL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class DebugLevel:
    DISABLE    = 0x0
    CRITICAL   = 0x1
    ERROR      = 0x2
    WARNING    = 0x4
    INFOMATION = 0x8
    DEBUG      = 0x10
    TRACE      = 0x10
    MAX        = 0xff

class RetValue:
    ERROR = -1
    SUCCESS = 0

# test funcion could sync all ins
class DebugSetting(object):

    debug_level = DebugLevel.CRITICAL | DebugLevel.ERROR
    debug_tag = "Disable"

    # @property
    # def debug_level(self):
    #     print('get debug_level')
    #     return type(self)._debug_level

    # @debug_level.setter
    # def debug_level(self,val):
    #     print('set debug_level')
    #     type(self)._debug_level = val
    @staticmethod
    def setDbgLevel(dbg_level):
        dbg_info(dbg_level)

        if "all"    == dbg_level:
            DebugSetting.debug_level = DebugLevel.MAX
        elif "default" == dbg_level:
            DebugSetting.debug_level = DebugLevel.CRITICAL | DebugLevel.ERROR
        elif "develoment" == dbg_level:
            DebugSetting.debug_level = DebugLevel.CRITICAL | DebugLevel.ERROR | DebugLevel.WARNING | DebugLevel.DEBUG | DebugLevel.INFOMATION

        elif "Disable"    == dbg_level:
            DebugSetting.debug_level = DebugLevel.DISABLE
        elif "Critical"   == dbg_level:
            DebugSetting.debug_level = DebugLevel.CRITICAL
        elif "Error"      == dbg_level:
            DebugSetting.debug_level = DebugLevel.CRITICAL | DebugLevel.ERROR
        elif "Warning"    == dbg_level:
            DebugSetting.debug_level = DebugLevel.CRITICAL | DebugLevel.ERROR | DebugLevel.WARNING
        elif "Infomation" == dbg_level:
            DebugSetting.debug_level = DebugLevel.CRITICAL | DebugLevel.ERROR | DebugLevel.WARNING | DebugLevel.INFOMATION
        elif "Debug"      == dbg_level:
            DebugSetting.debug_level = DebugLevel.CRITICAL | DebugLevel.ERROR | DebugLevel.WARNING | DebugLevel.INFOMATION | DebugLevel.DEBUG
        elif "Trace"      == dbg_level:
            DebugSetting.debug_level = DebugLevel.TRACE

        elif "disable"    == dbg_level:
            DebugSetting.debug_level = DebugLevel.DISABLE
        elif "critical"   == dbg_level:
            DebugSetting.debug_level |= DebugLevel.CRITICAL
        elif "error"      == dbg_level:
            DebugSetting.debug_level |= DebugLevel.ERROR
        elif "warning"    == dbg_level:
            DebugSetting.debug_level |= DebugLevel.WARNING
        elif "infomation" == dbg_level:
            DebugSetting.debug_level |= DebugLevel.INFOMATION
        elif "debug"      == dbg_level:
            DebugSetting.debug_level |= DebugLevel.DEBUG
        elif "trace"      == dbg_level:
            DebugSetting.debug_level |= DebugLevel.TRACE
        else:
            dbg_error('Wrong log level: ' + dbg_level)
            return False

        DebugSetting.debug_tag = dbg_level
        # print('Debug level:', DebugSetting.debug_level)
        return True
    @staticmethod
    def debuglevel(args):
        dbg_info(args)
        arg_dict = args
        arg_key = list(arg_dict.keys())
        if 'arg_1' not in arg_key:
            dbg_error('Not args found. log key: ' + arg_key)
            DebugSetting.dbg_show()
            return True

        log_level = arg_dict['arg_1']
        ret = DebugSetting.setDbgLevel(log_level)

        # print('Debug level:', DebugSetting.debug_level)
        DebugSetting.dbg_show()
        return True

    @staticmethod
    def getDbgTag():
        return DebugSetting.debug_tag
    @staticmethod
    def dbg_show():
        dbg_trace('trace')
        dbg_debug('debug')
        dbg_info('info')
        dbg_warning('warning')
        dbg_error('error')
        dbg_critical('critical')


# print(DebugSetting._debug_level)
# DebugSetting.debug_level = DebugLevel.CRITICAL | DebugLevel.ERROR | DebugLevel.INFOMATION
# TODO REMOVE this var
# DebugSetting.debug_level = DebugLevel.CRITICAL | DebugLevel.ERROR | DebugLevel.INFOMATION
# DebugSetting.debug_level = DebugLevel.MAX
def dbg_trace(*args):
    if DebugSetting.debug_level & DebugLevel.DEBUG > 0:
        dbg_print(Bcolors.TRACE, "[TRC] ", *args, Bcolors.ENDC)
def dbg_debug(*args):
    if DebugSetting.debug_level & DebugLevel.DEBUG > 0:
        dbg_print(Bcolors.ENDC, "[DBG] ", *args, Bcolors.ENDC)
def dbg_info(*args):
    if DebugSetting.debug_level & DebugLevel.INFOMATION > 0:
        dbg_print(Bcolors.OKGREEN, "[INF] ", *args, Bcolors.ENDC)
def dbg_warning(*args):
    if DebugSetting.debug_level & DebugLevel.WARNING > 0:
        dbg_print(Bcolors.WARNING, "[WARN] ", *args, Bcolors.ENDC)
def dbg_error(*args):
    if DebugSetting.debug_level & DebugLevel.ERROR > 0:
        dbg_print(Bcolors.ERROR, "[ERR] ", *args, Bcolors.ENDC)
def dbg_critical(*args):
    if DebugSetting.debug_level & DebugLevel.CRITICAL > 0:
        dbg_print(Bcolors.BOLD, Bcolors.CRITICAL, "[CRIT] ", *args, Bcolors.ENDC)

def dbgprint(*args):
    dbg_print(*args)
def dbg_print(*args):
    # print('Debug level:', DebugSetting.debug_level)
    timestamp = strftime("%d-%H:%M", gmtime())
    caller_frame = inspect.stack()[2]

    caller_filename = os.path.splitext(os.path.basename(caller_frame.filename))[0]
    caller_function = caller_frame.function
    caller_line_no = caller_frame.lineno

    print("[{}][{}][{}][{}]".format(timestamp, caller_filename, caller_function, caller_line_no) + "".join(map(str,args)))

