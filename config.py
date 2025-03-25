import sys
import os
import inspect
import json
import traceback
from configparser import ConfigParser
try:
    from utility.debug import *
except:
    from debug import *

class AppConfig:
    # Read only variable
    config_file = "./config.json"
    log_level = "Information"
    def __init__(self):
        _args = {}
    # class _args:
    #     clip_mode = ''
    class about:
        program_name = 'Config Manager'
        version='0.1.0'

    def get_args(self) -> str:
        """Getter for args"""
        return self._name

    def set_args(self, value: str):
        """Setter for name with basic validation"""
        if not value:
            raise ValueError("Name cannot be empty.")
        self._name = value

class ConfigManager:
    def __init__(self, config):
        self.config = config
    def _dump(self, instance, indent=''):
        indent_unit = 2 * ' '
        title_width = 20 - len(indent)

        ins_dict = vars(instance)
        dbg_debug(ins_dict)
        for each_key in ins_dict.keys():
            if each_key.startswith('_') is not True and type(ins_dict[each_key]).__name__  != 'function':
                if inspect.isclass(ins_dict[each_key]):
                    print('{}[{}]'.format(indent, each_key))
                    self._dump(ins_dict[each_key], indent + indent_unit)
                else:
                    print('{}{}: {}'.format(indent, each_key.ljust(title_width), ins_dict[each_key]))
    def dump(self, indent=''):
        self._dump(self.config, indent)

    def _dict(self, instance, indent=''):
        indent_unit = 2 * ' '
        title_width = 20 - len(indent)

        ins_dict = vars(instance)
        ret_dict = dict()
        for each_key in ins_dict.keys():
            if each_key.startswith('_') is not True and type(ins_dict[each_key]).__name__  != 'function':
                if inspect.isclass(ins_dict[each_key]):
                    # print('{}[{}]'.format(indent, each_key))
                    ret_dict[each_key] = self._dict(ins_dict[each_key], indent + indent_unit)
                else:
                    # print('{}{}: {}'.format(indent, each_key.ljust(title_width), ins_dict[each_key]))
                    ret_dict[each_key] = ins_dict[each_key]
        return ret_dict
    def toDict(self, indent=''):
        return self._dict(self.config, indent)
    def toJson(self):
        tmp_json = json.dumps(self.toDict(), indent=2)
        # dbg_debug(tmp_json.__str__())
        return tmp_json

    def save(self):
        dbg_info('Saving config file: {}'.format(self.config.config_file))
        with open(self.config.config_file, 'w') as configfile:
            configfile.write(self.toJson().__str__())
    def _loadDict(self, instance, cfg_dict):
        for each_key in cfg_dict.keys():
            if type(cfg_dict[each_key]).__name__ == 'str':
                # self.config.__dict__[each_key] = cfg_dict[each_key]
                setattr(instance, each_key, cfg_dict[each_key])
            elif type(cfg_dict[each_key]).__name__ == 'dict':
                # self._loadDict(getattr(instance, each_key) ,cfg_dict[each_key])
                self._loadDict(instance.__dict__[each_key] ,cfg_dict[each_key])
    def loadDict(self, cfg_dict):
        # dbg_print(self.dump())
        for each_key in cfg_dict.keys():
            try:
                if type(cfg_dict[each_key]).__name__ == 'str':
                    continue
                elif type(cfg_dict[each_key]).__name__ == 'dict':
                    # dbg_print(each_key, ', ', getattr(self.config, each_key))
                    tmp_ins = self.config.__dict__[each_key]

                    self._loadDict(tmp_ins, cfg_dict[each_key])
            except Exception as e:
                dbg_warning(e)

                traceback_output = traceback.format_exc()
                dbg_warning(traceback_output)
    def load(self, config_path=None):
        if config_path is None:
            config_path = self.config.config_file
        try:
            with open(config_path, 'r') as configfile:
                dbg_info('load config file from: {}'.format(config_path))
                cfg_buffer = configfile.read()
                tmp_json = json.loads(cfg_buffer)
                self.loadDict(tmp_json)
        except Exception as e:
            dbg_error(e)
            traceback_output = traceback.format_exc()
            dbg_error(traceback_output)

    # def get(self, key: str, default: Optional[Any] = None) -> Any:
    def get(self, key: str, default = None):
        """
        Support getting values via dot notation, e.g., 'audio.volume'
        """
        parts = key.split(".")
        obj = self.config
        for part in parts:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                return default
        return obj

    def set(self, key: str, value) -> None:
        """
        Support setting values via dot notation, e.g., 'audio.volume'
        """
        parts = key.split(".")
        obj = self.config
        for part in parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                raise AttributeError(f"Invalid config path: {key}")
        final_key = parts[-1]
        if hasattr(obj, final_key):
            setattr(obj, final_key, value)
            self.save()
        else:
            raise AttributeError(f"Invalid config field: {final_key}")



if __name__ == "__main__":
    cm = ConfigManager(AppConfig)
    cm.config.about.program_name = 'Clip Test Program.'
    print("## Dump Config")
    cm.dump() 
    print("")
    print("## Getting Info with dot.")
    print(f"program_name : {cm.config.about.program_name}")
    print(f"version      : {cm.config.about.version}")
    print("")

    print("## Set Info with function.")
    print(f"Before program_name : {cm.get('about.program_name')}")
    cm.set('about.program_name', 'Clip Test Changed.')
    print(f"After program_name : {cm.get('about.program_name')}")
    print("")

    print("## Get Info with function.")
    print(f"program_name : {cm.get('about.program_name')}")
    print(f"version      : {cm.get('about.version')}")
    print("")

    print("## Dump Info")
    print(cm.toDict()) 
