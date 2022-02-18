import settings
from utils.utils import read_config, load_plugins, log_string
from utils.hbase import save_to_hbase
from utils.kafka import read_from_kafka
from utils.mongo import mongo_logger

if __name__ == '__main__':
    config = read_config(settings.conf_file)
    sources_available = load_plugins()
    consumer = read_from_kafka(config['kafka']['topic'], config['kafka']['group_store'], config['kafka']['connection'])
    for m in consumer:
        m.commit()
        print("processing_message")
        message = m.value
        if 'logger' in message:
            mongo_logger.import_log(message['logger'], "store")
        message_part = ""
        if 'message_part' in message:
            message_part = message['message_part']

        log_string(f"received part {message_part} from {message['source']} to store")
        table = None
        for k, v in sources_available.items():
            if message['source'] == k:
                log_string(f"{k}, {v}, {message['source']}")
                table = v.get_store_table(message)
                break
        if table:
            try:
                save_to_hbase(message['data'], table, config['hbase_store_raw_data'], [("info", "all")],
                              row_fields=message['row_keys'])
                mongo_logger.log(f"part {message_part} successfully stored to HBASE")
            except Exception as e:
                mongo_logger.log(f"error storing part {message_part} to HBASE: {e}")
