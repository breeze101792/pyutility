import datetime
import os

from utility.debug import *

class Log:
    def __init__(self):
        dbg_debug('Console init')
        self.__log_fd = None
        self.__open_name = None

        if os.name == 'nt':
            self.sep = '\\'
        else:
            self.sep = '/'

    def __del__(self):
        self.close()
    def open(self, log_file_name='./terminal', path='./log'):
        now = datetime.datetime.now()
        timestamp = now.strftime('%Y%m%d_%H%M%S')

        if os.path.exists(path) is not True:
            os.mkdir(path)

        self.__open_name = path + self.sep + log_file_name + '_' + timestamp + '.log'

        dbg_debug('open file: ', self.__open_name)
        try:
            self.__log_fd = open(self.__open_name, "wb")
            self.__log_fd.write(('Record Start: ' + now.strftime('%Y-%m-%d %H:%M:%S').__str__() + '\n').encode())
            self.__log_fd.write('================================================================\n'.encode())

            # self.__log_fd.write("Now the file has more content!")
        except IOError:
            dbg_error('File open error')
            # self.__log_fd.close()
            self.__log_fd = None
        #open and read the file after the appending:
    def close(self):
        dbg_debug('close')
        if self.__log_fd is None:
            dbg_error('File not opened')
        else:
            now = datetime.datetime.now()
            self.__log_fd.write('\n================================================================\n'.encode())
            self.__log_fd.write(('Record End: ' + now.strftime('%Y-%m-%d %H:%M:%S').__str__() + '\n').encode())
            self.__log_fd.close()
            self.__log_fd = None

    def write(self, bufferbyte):
        dbg_debug('Write: ', bufferbyte)
        # Accept only byte
        if self.__log_fd is None:
            dbg_error('File not opened')
            return
        try:
            self.__log_fd.write(bufferbyte)
        except IOError:
            dbg_error('File write error')
    def isFileOpened(self):
        if self.__log_fd is None:
            dbg_error('File not opened')
            return False
        else:
            return True
    # def read(self):
    #     dbg_debug('Read Char')
    #     # self.__log_fd = open("demofile2.txt", "r")
    #     # print(self.__log_fd.read())
    #     # return 'r'.encode()
    #     return None
    # def readline(self):
    #     dbg_debug('Read line')
    #     # self.__log_fd = open("demofile2.txt", "r")
    #     # print(self.__log_fd.read())
    #     # return 'Readline\n'
    #     return None
