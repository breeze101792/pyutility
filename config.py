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

class BasicConfig:
    # log_level = "Information"
    class about:
        program_name = 'ConfigManager'
        version='0.1.0'
    class path:
        root = os.path.expanduser(f"~/.config/ConfigManager")
        config = "config.json"
        data = "data"
        log = "log"
    class variable:
        # share variable for instance, this will not be saved.
        pass

    # Persistant config, Add conig on other class.
    # class config:
    #     pass

    # Function
    def get_args(self) -> str:
        """Getter for args"""
        return self._name

    def set_args(self, value: str):
        """Setter for name with basic validation"""
        if not value:
            raise ValueError("Name cannot be empty.")
        self._name = value

class ConfigManager:
    def __init__(self, config, config_file = None):

        self.config = config
        self.internal_config_list = ['about', 'path', 'variable']

        if config_file is not None:
            self.load(config_file=config_file)

        # some config could be seeting here. before load, please use save=False
        # or your may orverwrite config file.
        # self.config.set_config(self.config, 'testconfig', save=False)
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
        # Construct the full path
        config_file = os.path.expanduser(os.path.join(self.config.path.root, self.config.path.config))
        dbg_debug('Saving config file to: {}'.format(config_file))

        # Ensure the target directory exists
        try:
            config_dir = os.path.dirname(config_file)
            if not os.path.isdir(config_dir):
                dbg_info(f"Config directory not found, creating: {config_dir}")
                os.makedirs(config_dir, exist_ok=True)
        except OSError as e:
            # Handle potential errors during directory creation (e.g., permissions)
            dbg_error(f"Error creating directory {config_dir}: {e}")
            traceback.print_exc()
            # Optionally re-raise the exception or return if saving is critical
            return # Or raise e

        # Write the config file
        try:
            with open(config_file, 'w') as configfile:
                config_dict = self.toDict()
                for each_internal_config in self.internal_config_list:
                    if each_internal_config in config_dict:
                        del config_dict[each_internal_config]
                configfile.write(json.dumps(config_dict, indent=2))
        except IOError as e:
            dbg_error(f"Error writing config file {config_file}: {e}")
            traceback.print_exc()
            # Optionally re-raise
    def _loadDict(self, instance, cfg_dict):
        for each_key in cfg_dict.keys():
            try:
                if type(cfg_dict[each_key]).__name__ == 'str':
                    # self.config.__dict__[each_key] = cfg_dict[each_key]
                    setattr(instance, each_key, cfg_dict[each_key])
                elif type(cfg_dict[each_key]).__name__ == 'dict':
                    # self._loadDict(getattr(instance, each_key) ,cfg_dict[each_key])
                    self._loadDict(instance.__dict__[each_key] ,cfg_dict[each_key])
            except Exception as e:
                dbg_warning(e)

                traceback_output = traceback.format_exc()
                dbg_warning(traceback_output)
    def loadDict(self, cfg_dict):
        for each_key in cfg_dict.keys():
            try:
                if type(cfg_dict[each_key]).__name__ == 'str':
                    continue
                elif type(cfg_dict[each_key]).__name__ == 'dict':
                    dbg_debug(each_key, ', ', getattr(self.config, each_key))
                    tmp_ins = self.config.__dict__[each_key]

                    self._loadDict(tmp_ins, cfg_dict[each_key])
            except Exception as e:
                dbg_warning(e)

                traceback_output = traceback.format_exc()
                dbg_warning(traceback_output)
    def load(self, config_file = None, config_path=None):
        # path
        if config_path is None:
            config_path = self.config.path.root
        config_path = os.path.expanduser(config_path)

        # file.
        if config_file is not None:
            config_file = config_file
        else:
            config_file = os.path.join(config_path, self.config.path.config)

        config_file = os.path.expanduser(config_file)

        # Check if file exists
        if not os.path.isfile(config_file):
            dbg_info(f"Config file not found, skipping load: {config_file}")
            return

        # Proceed with loading if directory and file exist
        try:
            with open(config_file, 'r') as configfile:
                dbg_info('Loading config file from: {}'.format(config_file))
                cfg_buffer = configfile.read()
                tmp_json = json.loads(cfg_buffer)
                dbg_debug(f"Load json: {tmp_json}")
                self.loadDict(tmp_json)
        # Keep specific FileNotFoundError for clarity, though covered by isfile check
        except FileNotFoundError:
             # This case should ideally not be reached due to the isfile check above,
             # but kept for robustness against race conditions or unexpected issues.
            dbg_warning(f"Config file disappeared unexpectedly: {config_file}")
        except json.JSONDecodeError as e:
            dbg_error(f"Error decoding JSON from config file {config_file}: {e}")
            traceback.print_exc()
        except Exception as e:
            dbg_error(f"An unexpected error occurred during config load from {config_file}: {e}")
            traceback.print_exc()

    def get_path(self, key: str, default = None):
        """
        Retrieves a path configuration value by key from the 'path' section,
        joins it with the root path, and returns the full path.

        Args:
            key (str): The key for the path variable within config.path (e.g., 'data', 'log').
            default: The value to return if the key is not found. Defaults to None.

        Returns:
            str or default: The full, joined path, or the default value if the key is not found.
        """
        path_config = self.config.path
        if hasattr(path_config, key):
            path_value = getattr(path_config, key)

            # Check if the retrieved value is a string
            if isinstance(path_value, str):
                # Check if the path value is absolute or start with '/' and '.' (interpreted as full path)
                if os.path.isabs(path_value) or '/' == path_value[0] or '.' == path_value[0] :
                    dbg_debug(f"Path key '{key}' value '{path_value}' is absolute or contains '/'. Returning directly.")
                    return os.path.expanduser(path_value)
                else:
                    # It's considered a relative path, try to join with root
                    root_path = os.path.expanduser(path_config.root)
                    if isinstance(root_path, str):
                        return os.path.join(root_path, path_value)
                    else:
                        dbg_warning(f"Cannot join paths: root='{root_path}' (type: {type(root_path)}) is not a string for relative path key='{key}' value='{path_value}'")
                        return default
            else:
                # Value associated with key is not a string
                dbg_warning(f"Path key '{key}' value '{path_value}' (type: {type(path_value)}) is not a string.")
                return default
        else:
            # Key not found in path_config
            dbg_info(f"Path key '{key}' not found in config.path section.")
            return default
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

    def set(self, key: str, value, save = True) -> None:
        """
        Support setting values via dot notation, e.g., 'audio.volume'
        """
        dbg_debug(f"Set '{key}' to '{value}', svae:{save}")
        parts = key.split(".")
        # chek if it's instance config, then we don't need to save it.
        if len(parts) != 0 and parts[0] in self.internal_config_list:
            save = False

        obj = self.config
        for part in parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                raise AttributeError(f"Invalid config path: {key}")
        final_key = parts[-1]
        if hasattr(obj, final_key):
            setattr(obj, final_key, value)
            if save is True:
                self.save()
        else:
            raise AttributeError(f"Invalid config field: {final_key}")
    def dump(self, args = None) -> bool:
        # this is for command line use.
        print(self.toJson())
        return True

if __name__ == "__main__":
    # python -m utility.config
    cm = ConfigManager(BasicConfig)
    cm.config.about.program_name = 'Clip Test Program.'
    print("## Dump Config")
    cm.dump() 
    print("")
    print("## Getting Info with dot.")
    print(f"program_name : {cm.config.about.program_name}")
    print(f"version      : {cm.config.about.version}")
    print(f"root         : {cm.get_path('root')}")
    print(f"data         : {cm.get_path('data')}")
    print(f"log          : {cm.get_path('log')}")
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
