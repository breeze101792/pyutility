from utility.debug import *
import datetime
class Log:
    def __init__(self):
        dbg_debug('Console init')
        self.__log_fd = None
        self.__open_name = None

    def __del__(self):
        self.close()
    def open(self, path_name='./terminal'):
        now = datetime.datetime.now()
        timestamp = now.strftime('%Y%m%d_%H%M%S')
        self.__open_name = path_name + '_' + timestamp + '.log'

        dbg_debug('open file: ', self.__open_name)
        try:
            self.__log_fd = open(self.__open_name, "w")
            self.__log_fd.write('Record Start: ' + now.strftime('%Y-%m-%d %H:%M:%S').__str__() + '\n')
            self.__log_fd.write('================================================================\n')

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
            self.__log_fd.write('\n================================================================\n')
            self.__log_fd.write('Record End: ' + now.strftime('%Y-%m-%d %H:%M:%S').__str__() + '\n')
            self.__log_fd.close()
            self.__log_fd = None

    def write(self, bufbyte):
        dbg_debug('Write: ', bufbyte)
        # Accept only byte
        if self.__log_fd is None:
            dbg_error('File not opened')
            return
        try:
            self.__log_fd.write(bufbyte)
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
