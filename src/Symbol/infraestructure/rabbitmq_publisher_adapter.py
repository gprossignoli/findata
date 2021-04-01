from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from pika.exceptions import ChannelError
import ujson

from src.Symbol.domain.symbol import Symbol
from src.Symbol.domain.ports.symbol_publisher_interface import SymbolPublisherInterface
from src import settings as st


class RabbitException(Exception):
    pass


class RabbitmqPublisherAdapter(SymbolPublisherInterface):
    def __init__(self):
        self.connection = self.__connect_to_rabbit()

    def publish_symbols(self, symbols: tuple[Symbol, ...]) -> None:
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
        connection = BlockingConnection(
            ConnectionParameters(host=st.MONGO_HOST, port=st.RABBIT_PORT,
                                 virtual_host=st.RABBIT_VHOST, credentials=credentials))
        channel = connection.channel()

        try:
            channel.exchange_declare(exchange=st.SYMBOLS_HISTORY_EXCHANGE, exchange_type='topic')
        except ChannelError as e:
            st.logger.exception(e)
            raise RabbitException()
        return connection

    @staticmethod
    def __adapt_symbol_historic(historical_data):
        return historical_data.to_dict()

