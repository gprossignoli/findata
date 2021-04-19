import logging
import os
import configparser
from logging.handlers import RotatingFileHandler

ROOT_DIR = os.path.dirname(os.path.abspath("settings.py"))
settings_file = open(os.path.join(ROOT_DIR, "settings.ini"), "r")
config = configparser.ConfigParser()
config.read(os.path.join(ROOT_DIR, "settings.ini"))

MONGO_HOST, MONGO_PORT = config.get("DB", "mongo_db").split(":")


# LOGGING CONFIG

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('findata')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# to log debug messages
debug_logger = logging.StreamHandler()
debug_logger.setLevel(logging.DEBUG)
debug_logger.setFormatter(formatter)

# to log general messages
# x2 files of 2mb
info_logger = RotatingFileHandler(filename='findata.log', maxBytes=2097152, backupCount=2)
info_logger.setLevel(logging.INFO)
info_logger.setFormatter(formatter)

#to log errors messages
error_logger = RotatingFileHandler(filename='findata_errors.log', maxBytes=2097152, backupCount=2)
error_logger.setLevel(logging.ERROR)
error_logger.setFormatter(formatter)

logger.addHandler(debug_logger)
logger.addHandler(info_logger)
logger.addHandler(error_logger)

# ObtainExchangeTickersUseCase
# Ibex35, S&P500, Dow Jones, Nasdaq, Euro stoxx50, EURONEXT100, IBEX Medium Cap.
exchanges = ('^IBEX', '^GSPC', '^DJI', '^IXIC', '^STOXX50E', '^N100', 'INDC.MC')

# Rabbitmq data
RABBIT_HOST = config.get("RABBIT", "rabbit_host")
RABBIT_PORT = config.get("RABBIT", "rabbit_port")
RABBIT_USER = config.get("RABBIT", "rabbit_user")
RABBIT_PASSW = config.get("RABBIT", "rabbit_password")
RABBIT_VHOST = config.get("RABBIT", "rabbit_vhost")

SYMBOLS_HISTORY_EXCHANGE = 'findata_symbols'
SYMBOL_HISTORY_ROUTING_KEY = 'findata.symbol'
STOCKS_HISTORY_ROUTING_KEY = 'findata.symbol.stock'
INDEXES_HISTORY_ROUTING_KEY = 'findata.symbol.index'
