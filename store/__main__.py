import time
import settings
from utils.utils import read_config, load_plugins, log_string
from utils.hbase import save_to_hbase
from utils.kafka import read_from_kafka
from utils.mongo import mongo_logger

if __name__ == '__main__':
    config = read_config(settings.conf_file)
    sources_available = load_plugins(settings)
    consumer = read_from_kafka(config['kafka']['topic'], config['kafka']['group_store'], config['kafka']['connection'])
    try:
        for x in consumer:
            message = x.value
            if 'logger' in message:
                mongo_logger.import_log(message['logger'], "store")
            message_part = ""
            if 'message_part' in message:
                message_part = message['message_part']

            table = None
            for k, v in sources_available.items():
                if message['source'] == k:
                    table = v.get_store_table(message)
                    break
            if table:
                try:
                    save_to_hbase(message['data'], table, config['hbase_store_raw_data'], [("info", "all")],
                                  row_fields=message['row_keys'])
                    log_string(f"part {message_part} successfully stored to HBASE", mongo=False)
                except Exception as e:
                    log_string(f"error storing part {message_part} to HBASE: {e}")
    except Exception as e:
        time.sleep(10)
        print(e)
