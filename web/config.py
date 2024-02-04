import configparser


def dict_param(param_str):
    return {el.split(':')[0]: el.split(':')[1] for el in param_str.split(', ')}


config = configparser.ConfigParser()
config.read("config_front.cfg", encoding="utf-8")

exts = config.get('Files and directories', 'extensions').split(', ')
data_path = config.get('Files and directories', 'data_path')

check_time = config.getint('Working parameters', 'check_time')
secret_key = open(config.get('Working parameters', 'secret_key_file'), encoding="utf-8").read()
verbose = config.get('Working parameters', 'verbose')
if verbose == 'False':  # для консистентности: везде строки
    verbose = ''
port = config.getint('Working parameters', 'port')
debug = config.getboolean('Working parameters', 'debug')

method2name = dict_param(config.get('Search parameters', 'methods'))

params = {'methods': method2name,
          # 'sm_funcs': dict_param(config.get('Search parameters', 'sm_funcs')),
          'rounding_min': config.getint('Search parameters', 'rounding_min'),
          'rounding_max': config.getint('Search parameters', 'rounding_max'),
          }

def_params = {'method': config.get('Default parameters', 'def_method'),
              # 'sm_func': config.get('Default parameters', 'def_sm_func'),
              'rounding': config.get('Default parameters', 'def_rounding'),
              'tok_forced': config.getboolean('Default parameters', 'def_tok_forced'),
              'prep_forced': config.getboolean('Default parameters', 'def_prep_forced'),
              'test': config.getboolean('Default parameters', 'def_test'),
              }

metric2name = dict_param(config.get('Eval parameters', 'metrics'))
