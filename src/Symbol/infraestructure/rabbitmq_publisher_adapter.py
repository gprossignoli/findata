import socket

from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from pika.exceptions import AMQPConnectionError, AMQPChannelError
import ujson

from src.Symbol.domain.symbol import Symbol, Stock
from src.Symbol.domain.ports.symbol_publisher_interface import SymbolPublisherInterface
from src.Utils.exceptions import PublisherException
from src import settings as st


class RabbitmqPublisherAdapter(SymbolPublisherInterface):
    def __init__(self):
        self.connection = None

    def publish_symbols(self, symbols: tuple[Symbol, ...]) -> None:
        if self.connection is None:
            self.connection = self.__connect_to_rabbit()

        st.logger.info("Publishing symbols: {}".format([s.ticker for s in symbols]))
        conn_channel = self.connection.channel()
        for symbol in symbols:
            adapted_historic = self.__adapt_stock_historic(symbol.historical_data)
            if isinstance(symbol, Stock):
                message = {
                    'ticker': symbol.ticker,
                    'isin': symbol.isin,
                    'name': symbol.name,
                    'historic': adapted_historic,
                    'exchange': symbol.exchange
                }
                routing_key = st.STOCKS_HISTORY_ROUTING_KEY
            else:
                message = {
                    'ticker': symbol.ticker,
                    'isin': symbol.isin,
                    'name': symbol.name,
                    'historic': adapted_historic
                }
                routing_key = st.SYMBOL_HISTORY_ROUTING_KEY
            message = ujson.dumps(message)
            try:
                conn_channel.basic_publish(exchange=st.SYMBOLS_HISTORY_EXCHANGE,
                                           routing_key=routing_key,
                                           body=message)
            except Exception as e:
                st.logger.exception(e)
                pass

    def publish_indexes(self, indexes: tuple[Symbol, ...]) -> None:
        if self.connection is None:
            self.connection = self.__connect_to_rabbit()

        st.logger.info("Publishing indexes: {}".format([s.ticker for s in indexes]))
        conn_channel = self.connection.channel()
        for index in indexes:
            adapted_historic = self.__adapt_index_historic(index.historical_data)
            message = {
                'ticker': index.ticker,
                'isin': index.isin,
                'name': index.name,
                'historic': adapted_historic
            }
            message = ujson.dumps(message)
            try:
                conn_channel.basic_publish(exchange=st.SYMBOLS_HISTORY_EXCHANGE,
                                           routing_key=st.INDEXES_HISTORY_ROUTING_KEY,
                                           body=message)
            except Exception as e:
                st.logger.exception(e)
                pass

    @staticmethod
    def __connect_to_rabbit() -> BlockingConnection:
        """
        Opens the connection to rabbit, and prepares the exchange to be used.
        """
        st.logger.info("Connecting to rabbitmq")
        credentials = PlainCredentials(username=st.RABBIT_USER, password=st.RABBIT_PASSW)
        try:
            connection = BlockingConnection(
                ConnectionParameters(host=st.RABBIT_HOST, port=st.RABBIT_PORT,
                                     virtual_host=st.RABBIT_VHOST, credentials=credentials,
                                     connection_attempts=5,
                                     retry_delay=3))
        except (AMQPConnectionError, socket.gaierror) as e:
            st.logger.exception(e)
            raise PublisherException()

        try:
            channel = connection.channel()
            channel.exchange_declare(exchange=st.SYMBOLS_HISTORY_EXCHANGE, exchange_type='topic')
        except AMQPChannelError as e:
            st.logger.exception(e)
            raise PublisherException()

        return connection

    @staticmethod
    def __adapt_stock_historic(historical_data):
        historical_data = historical_data.rename(columns={"Open": "open", "Close": "close", "High": "high",
                                                          "Low": "low", "Dividends": "dividends", "Volume": "volume"})
        return historical_data.to_dict()

    @staticmethod
    def __adapt_index_historic(historical_data):
        historical_data = historical_data.rename(columns={"Open": "open", "Close": "close", "High": "high",
                                                          "Low": "low"})
        return historical_data.to_dict()
