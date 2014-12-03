# coding:utf-8
import sys
import time
import json
import logging
import traceback

import pika

logging.basicConfig()
logger = logging.getLogger("MQ")


class MessageClient(object):

    def __init__(self, config):
        self.exchange_type = 'direct'
        self.receiving = True
        self.passing = True

        self.rabbitmq_server = config.get('RABBITMQ_SERVER')
        self.rabbitmq_port = config.get('RABBITMQ_PORT')
        self.rabbitmq_virtual_host = config.get('RABBITMQ_VHOST')
        self.rabbitmq_auth_user = config.get('RABBITMQ_USER')
        self.rabbitmq_auth_pwd = config.get('RABBITMQ_PASS')
        self.exchange_name = config.get('MQ_EXCHANGE')
        self.in_routing_key = config.get('MQ_INKEY')
        self.in_queue_name = config.get('MQ_INQUEUE')
        self.out_routing_key = config.get('MQ_OUTKEY')
        self.out_queue_name = config.get('MQ_OUTQUEUE')

        if not self.in_queue_name:
            self.receiving = False

        if not self.out_queue_name:
            self.passing = False

        self.rabbitmq_credentials = pika.PlainCredentials(self.rabbitmq_auth_user, self.rabbitmq_auth_pwd)

        self.recv_connection = None
        self.recv_channel = None
        self.send_channel = None

        self.recv_connection_available = True
        self.send_channel_available = True

        self.__init_Connection()

        # Chanel Configuration
        if self.receiving:
            self.__init_recvChannel()

        if self.passing:
            self.__init_sendChannel()

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)

    def __init_Connection(self):
        if not self.recv_connection or self.recv_connection.is_closed:
            self.recv_connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    credentials=self.rabbitmq_credentials,
                    host=self.rabbitmq_server,
                    port=self.rabbitmq_port,
                    virtual_host=self.rabbitmq_virtual_host,
                    #                heartbeat_interval = 2
                    #                channel_max=None,
                    #                frame_max=131072
                )
            )

        self.recv_connection_available = True

    def __init_recvChannel(self):
        if not self.recv_channel or self.recv_channel.is_closed:
            self.recv_channel = self.recv_connection.channel()
            self.recv_channel.exchange_declare(exchange=self.exchange_name,
                                               type=self.exchange_type,
                                               durable=True)
            self.recv_channel.queue_declare(queue=self.in_queue_name, durable=True)
            self.recv_channel.queue_bind(exchange=self.exchange_name,
                                         queue=self.in_queue_name,
                                         routing_key=self.in_routing_key)

    def __check_recvChannel(self):
        if not self.recv_connection or self.recv_connection.is_closed:
            self.__init_Connection()
        if not self.recv_channel or self.recv_channel.is_closed:
            self.__init_recvChannel()

    def __init_sendChannel(self):
        if not self.send_channel or self.send_channel.is_closed:
            self.send_channel = self.recv_connection.channel()
            self.send_channel.exchange_declare(exchange=self.exchange_name,
                                               type=self.exchange_type,
                                               durable=True)
        self.send_channel_available = True

    def __check_connection(self):
        if not self.recv_connection or self.recv_connection.is_closed:
            if self.recv_connection_available:
                self.recv_connection_available = False
                self.__init_Connection()
            else:
                while not self.recv_connection_available:
                    logger.warn('Other thread is opening recv_connection , wait 10s...')
                    time.sleep(10)
                if not self.recv_connection or self.recv_connection.is_closed:
                    logger.fatal('Oh!, recv connection is broken! exit !!!')
                    sys.exit()

    def __check_sendChannel(self):
        self.__check_connection()
        if not self.send_channel or self.send_channel.is_closed:
            if self.send_channel_available:
                self.send_channel_available = False
                logger.warn('send_channel is closed, reconnect.')
                self.__init_sendChannel()
            else:
                while not self.send_channel_available:
                    logger.warn('Other thread is opening send_channel , wait 10s...')
                    time.sleep(10)
                if not self.send_channel or self.send_channel.is_closed:
                    logger.fatal('Oh!, send channel is broken! exit !!!')
                    sys.exit()

    def __reconnect_sendChannel(self):
        if self.send_channel:
            self.send_channel.close()
            self.send_channel = None
        if self.recv_connection:
            self.recv_connection.close()
            self.recv_connection = None
        self.__init_Connection()
        self.__init_sendChannel()

    def consuming(self, callbackfunc):
        """consuming message useing callback function."""
        self.callbackfunction = callbackfunc
        if not self.receiving:
            return None

        def callback(ch, method, properties, body):
            data = json.loads(body, encoding='utf-8')
            try:
                new_data = self.callbackfunction(data)
            except Exception:
                new_data = data
            if self.passing and new_data is not None:
                self.send(new_data)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        self.recv_channel.basic_qos(prefetch_count=20)
        self.recv_channel.basic_consume(callback,
                                        queue=self.in_queue_name)
        self.recv_channel.start_consuming()

    def sendMsg(self, data, tryagain=False):
        """send message using separate channel
        return True/False
        """
        res = True
        self.__check_connection()
        __send_channel = self.recv_connection.channel()
        __send_channel.exchange_declare(exchange=self.exchange_name,
                                        type=self.exchange_type,
                                        durable=True)
        message = json.dumps(data, encoding='utf-8')
        try:
            __send_channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=self.out_routing_key,
                body=message,
                properties=pika.BasicProperties(delivery_mode=2))
        except Exception as e:
            res = False
            logger.error(e)
            traceback.print_exc()
        finally:
            __send_channel.close()
            logger.debug('Release channel.')

        return res

    def send(self, data, tryagain=False):
        """
        send message
        return True/False
        """
        res = True
        if not self.passing:
            return False
        message = json.dumps(data, encoding='utf-8')
        self.__check_sendChannel()
        try:
            self.send_channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=self.out_routing_key,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2))
        except Exception as e:
            res = False
            logger.error(e)
            traceback.print_exc()
            logger.fatal('Exit!')
            sys.exit()
        return res
