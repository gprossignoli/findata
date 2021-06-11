import os
import logging
from logging.handlers import RotatingFileHandler

from environ import environ

ROOT_DIR = os.path.dirname(os.path.abspath("settings.py"))
ENV_FILE = os.path.abspath(os.path.join(ROOT_DIR, ".env"))

env = environ.Env(
    MONGO_DB=(str, ""),
    MONGODB_USER=(str, ""),
    MONGODB_PASS=(str, ""),
    RABBIT_HOST=(str, ""),
    RABBIT_PORT=(int, None),
    RABBIT_USER=(str, ""),
    RABBIT_PASSWORD=(str, ""),
    RABBIT_VHOST=(str, ""),
)

env.read_env(ENV_FILE)


MONGO_HOST, MONGO_PORT = env("MONGO_DB").split(":")

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

# to log errors messages
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
RABBIT_HOST = env("RABBIT_HOST")
RABBIT_PORT = env("RABBIT_PORT")
RABBIT_USER = env("RABBIT_USER")
RABBIT_PASSW = env("RABBIT_PASSWORD")
RABBIT_VHOST = env("RABBIT_VHOST")

SYMBOLS_HISTORY_EXCHANGE = 'findata_symbols'
SYMBOL_HISTORY_ROUTING_KEY = 'findata.symbol'
STOCKS_HISTORY_ROUTING_KEY = 'findata.symbol.stock'
INDEXES_HISTORY_ROUTING_KEY = 'findata.symbol.index'
