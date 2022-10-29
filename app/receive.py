#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import pika
from pprint import pprint
from settings import (
    RABBITMQ_USERNAME,
    RABBITMQ_PASSWORD,
    RABBITMQ_HOST,
    )
from routers.logger import logger


PORT=5672
RABBITMQ_QUEUE = 'test_queue'
credentials = pika.PlainCredentials(
    username=RABBITMQ_USERNAME,
    password=RABBITMQ_PASSWORD)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=PORT,
        credentials=credentials)
    )

def receive_mess():
    """main method, connect and get messages from rabbitMQ"""
    logger.info('Connection start:')
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

    logger.info('[*] Waiting for logs. To exit press CTRL+C.')
    channel.basic_consume(
        queue=RABBITMQ_QUEUE, on_message_callback=callback)
    channel.start_consuming()

def callback(ch, method, properties, body):
    pprint(" [x] Received %r" % (json.loads(body),))
    ch.basic_ack(delivery_tag=method.delivery_tag)  # Отправить подтверждающее сообщение


if __name__ == '__main__':
    receive_mess()