import math
import pickle
from copy import deepcopy
from kafka import KafkaProducer, KafkaConsumer

from utils.utils import log_string


def save_to_kafka(topic, info_document, config, batch=1000):
    info_document = deepcopy(info_document)
    servers = [f"{host}:{port}" for host, port in zip(config['hosts'], config['ports'])]
    producer = KafkaProducer(bootstrap_servers=servers,
                             value_serializer=lambda v: pickle.dumps(v),
                             compression_type='gzip')
    data_message = info_document.pop("data")
    part = 1
    total = int(math.ceil(len(data_message)/batch))
    while data_message:
        send_message = deepcopy(info_document)
        send_message["data"] = data_message[:batch]
        data_message = data_message[batch:]
        send_message["message_part"] = f"{part}/{total}"
        f = producer.send(topic, value=send_message)
        f.get(timeout=10)
        part += 1


def read_from_kafka(topic, group_id, config):
    kafka_servers = [f"{host}:{port}" for host, port in zip(config['hosts'], config['ports'])]
    consumer = KafkaConsumer(topic, bootstrap_servers=kafka_servers, group_id=group_id,
                             value_deserializer=lambda v: pickle.loads(v))
    return consumer
