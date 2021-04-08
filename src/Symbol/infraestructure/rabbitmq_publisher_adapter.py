import socket

from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from pika.exceptions import AMQPConnectionError, AMQPChannelError
import ujson

from src.Symbol.domain.symbol import Symbol
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
            adapted_historic = self.__adapt_symbol_historic(symbol.historical_data)
            message = {
                'ticker': symbol.ticker,
                'isin': symbol.isin,
                'name': symbol.name,
                'historic': adapted_historic
            }
            message = ujson.dumps(message)
            try:
                conn_channel.basic_publish(exchange=st.SYMBOLS_HISTORY_EXCHANGE, routing_key='findata.symbol',
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
    def __adapt_symbol_historic(historical_data):
        historical_data = historical_data.rename(columns={"Open": "open", "Close": "close", "High": "high",
                                                          "Low": "low", "Dividends": "dividends", "Volume": "volume"})
        return historical_data.to_dict()
