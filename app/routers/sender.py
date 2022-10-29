#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import pika

from settings import (
    RABBITMQ_USERNAME,
    RABBITMQ_PASSWORD,
    RABBITMQ_HOST,
    )
from .logger import logger


EXCHANGE = 'test_api'
ROUTING_KEY = 'test_routing_key'
RABBITMQ_QUEUE = 'test_queue'
def send_message(body=''):
    """send message json to rabbitMQ"""

    logger.info(f"Start message to {RABBITMQ_QUEUE}.")
    credentials = pika.PlainCredentials(
        username=RABBITMQ_USERNAME,
        password=RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=credentials)
        )
    logger.info(f"Start connection.")
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE, exchange_type='direct', durable=True)
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    channel.queue_bind(
        exchange=EXCHANGE,
        queue=RABBITMQ_QUEUE,
        routing_key=ROUTING_KEY)
    logger.info(f"Start queue_bind.")
    channel.basic_publish(
        exchange=EXCHANGE,
        routing_key=ROUTING_KEY,
        body=body,
        properties=pika.BasicProperties(delivery_mode=1))
    connection.close()
    logger.info("Message for data preparer was sended to rabbitMQ.")
    